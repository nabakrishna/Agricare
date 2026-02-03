import { Octokit } from "@octokit/rest";

// Interfaces for Agricare Data Entities
interface FarmerProfile {
  id: string;
  name: string;
  location: string;
  crops: string[];
  joinedAt: string;
}

interface DiseaseReport {
  id: string;
  farmerId: string;
  cropType: string;
  aiDiagnosis: string;
  status: 'pending' | 'resolved' | 'escalated';
  timestamp: string;
}

/**
 * Agricare Admin Controller
 * Manages the connection between the UI and the GitHub-based data store.
 */
export class AgricareAdmin {
  private octokit: Octokit;
  private repoOwner: string;
  private repoName: string;

  constructor(token: string, owner: string, repo: string) {
    this.octokit = new Octokit({ auth: token });
    this.repoOwner = owner;
    this.repoName = repo;
  }

  // Fetch all registered users/farmers from the 'users/' directory
  async getFarmers(): Promise<FarmerProfile[]> {
    try {
      const { data } = await this.octokit.repos.getContent({
        owner: this.repoOwner,
        repo: this.repoName,
        path: 'data/users'
      });

      if (Array.isArray(data)) {
        const profiles = await Promise.all(
          data.map(async (file) => {
            const content = await this.getFileContent(file.path);
            return JSON.parse(content);
          })
        );
        return profiles;
      }
      return [];
    } catch (error) {
      console.error("Failed to fetch farmers:", error);
      throw error;
    }
  }

  // Monitor AI disease detection logs
  async getDiseaseReports(): Promise<DiseaseReport[]> {
    try {
      const { data } = await this.octokit.repos.getContent({
        owner: this.repoOwner,
        repo: this.repoName,
        path: 'data/reports'
      });

      if (Array.isArray(data)) {
        const reports = await Promise.all(
          data.map(async (file) => {
            const content = await this.getFileContent(file.path);
            return JSON.parse(content);
          })
        );
        return reports.sort((a, b) => b.timestamp.localeCompare(a.timestamp));
      }
      return [];
    } catch (error) {
      return [];
    }
  }

  // Update a report status (e.g., confirming an AI diagnosis)
  async updateReportStatus(reportId: string, status: string): Promise<void> {
    const path = `data/reports/${reportId}.json`;
    const currentFile = await this.octokit.repos.getContent({
      owner: this.repoOwner,
      repo: this.repoName,
      path: path
    });

    if ('sha' in currentFile.data) {
      const content = JSON.parse(atob(currentFile.data.content));
      content.status = status;

      await this.octokit.repos.createOrUpdateFileContents({
        owner: this.repoOwner,
        repo: this.repoName,
        path: path,
        message: `Admin: Updated report ${reportId} to ${status}`,
        content: btoa(JSON.stringify(content, null, 2)),
        sha: currentFile.data.sha
      });
    }
  }

  private async getFileContent(path: string): Promise<string> {
    const { data }: any = await this.octokit.repos.getContent({
      owner: this.repoOwner,
      repo: this.repoName,
      path: path
    });
    return atob(data.content);
  }
}
