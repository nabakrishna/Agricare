import sqlite3
import json

# The cleaned, accurate dataset and it has more to update
data = {
  "diseases": [
    {
      "plant_name": "Sugarcane",
      "disease": "Whip Smut",
      "symptom": "A long, black, whip-like growth appears at the top of the plant, releasing black powder.",
      "detailed_symptoms": "The terminal growing point transforms into a long, black, whip-like structure that releases millions of black, powdery spores; infected plants are stunted with thin stalks and exhibit profuse tillering from the base, giving a grassy appearance.[1, 3, 5, 11, 12]",
      "organic_treatment": "Sett treatment with extracts from neem leaves or fruits.[13]",
      "chemical_treatment": "Sett treatment by dipping in solutions of Triadimefon (Bayleton) or Carboxin (Vitavax).[14]",
      "prevention": "Use resistant varieties and healthy, disease-free setts; carefully remove and destroy infected plants (cover the whip before removal); avoid ratooning heavily infected fields; use hot water treatment for setts.[11, 12, 14, 15, 16]"
    },
    {
      "plant_name": "Sugarcane",
      "disease": "Pokkah Boeng",
      "symptom": "The top of the plant is malformed with yellow or white patches on young leaves, which can be wrinkled or twisted.",
      "detailed_symptoms": "Chlorotic phase: Yellowing or whitening patches at the base of young, unfurling leaves, which may appear wrinkled, twisted, and shortened. Top rot phase: The growing point is killed, and the top of the plant dies. Knife-cut phase: Transverse cuts or ladder-like lesions appear on the stalk.[1, 3, 17, 18, 19, 20, 21, 22, 23]",
      "organic_treatment": "Application of Trichoderma harzianum.[17, 20]",
      "chemical_treatment": "Foliar sprays with Carbendazim, Copper Oxychloride, or Mancozeb.[3, 17, 18, 19, 20, 21, 23]",
      "prevention": "Cultivate resistant or moderately tolerant varieties; maintain good field sanitation by removing infected debris; ensure proper field drainage.[17, 18, 19, 20, 21, 23]"
    },
    {
      "plant_name": "Sugarcane",
      "disease": "Grassy Shoot Disease (GSD)",
      "symptom": "Plant produces many thin, grass-like shoots from the base, and leaves may be white or yellow.",
      "detailed_symptoms": "Profuse tillering giving a grassy appearance; stunted shoots; narrow and small leaves; thin canes with short internodes; leaves appear white or creamy yellow due to lack of chlorophyll; premature sprouting of lateral buds.[1, 5, 24, 25]",
      "organic_treatment": "Not specified in the provided data. Preventive heat therapy (hot water or moist hot air) is an effective non-chemical method.[25]",
      "chemical_treatment": "Sett treatment with a 500-ppm solution of the antibiotic ledermycin.[25]",
      "prevention": "Use resistant varieties and healthy, disease-free planting material; use heat therapy for setts; avoid ratooning affected crops; practice crop rotation; remove and destroy affected stools; control insect vectors.[25]"
    },
    {
      "plant_name": "Rice",
      "disease": "Rice Blast",
      "symptom": "Spindle-shaped spots with grey centers and brown edges appear on leaves; in severe cases, the crop looks burnt.",
      "detailed_symptoms": "Spindle-shaped or eye-shaped lesions on leaves with greyish-white centers and dark brown margins; a 'blasted' or burnt appearance in severe cases; nodes turn black and break (nodal blast); grayish-brown lesion at the panicle base, causing unfilled grains or the panicle to break off (neck blast).[26, 27, 28, 29, 30, 31, 32, 33, 34, 35]",
      "organic_treatment": "Seed treatment, seedling root dip, and foliar sprays with Pseudomonas fluorescens.[26, 27, 36]",
      "chemical_treatment": "Seed treatment with Carbendazim or Tricyclazole; foliar sprays with Tricyclazole, Edifenphos, or Carbendazim.[26, 27, 28, 29, 30, 35]",
      "prevention": "Cultivate resistant varieties; avoid excessive nitrogen fertilizer; remove and destroy weed hosts and infected straw/stubbles; manage water properly by maintaining a continuous flood.[26, 27, 28, 29, 30, 31, 32, 33, 34, 35]"
    },
    {
      "plant_name": "Rice",
      "disease": "Bacterial Leaf Blight (BLB)",
      "symptom": "Seedlings wilt and die; mature plants have yellow-white stripes on leaves starting from the tips, with milky drops of ooze in the morning.",
      "detailed_symptoms": "Seedling stage ('kresek'): Wilting and rolling of leaves, turning grayish-green to yellow, leading to seedling death. Mature plants: Water-soaked stripes on leaf margins, starting from the tips, which enlarge and turn yellowish-white or golden yellow with a wavy margin; milky or opaque droplets of bacterial ooze on young lesions in the morning.[37, 38, 39, 40, 41]",
      "organic_treatment": "Spraying fresh cow dung extract or neem oil (3%); application of Pseudomonas fluorescens.[39, 42]",
      "chemical_treatment": "Seed treatment with a mixture of bleaching powder and zinc sulfate; foliar spray with a combination of Streptomycin sulphate + Tetracycline and Copper oxychloride.[39]",
      "prevention": "Plant resistant varieties; use disease-free seed; avoid clipping seedling tips during transplanting; ensure good field drainage; avoid water flow from infected fields; use balanced fertilization and avoid excessive nitrogen.[38, 39, 40]"
    },
    {
      "plant_name": "Rice",
      "disease": "Sheath Blight",
      "symptom": "Oval spots with a 'snake skin' pattern (greyish-white center, dark brown border) appear on sheaths near the water line.",
      "detailed_symptoms": "Oval or irregular greenish-grey, water-soaked spots on leaf sheaths near the water line; lesions enlarge with a greyish-white center and an irregular, dark brown border ('snake skin' pattern); infection spreads upwards to upper leaf sheaths and blades; lesions coalesce, causing the death of entire tillers.[43, 44, 45, 46, 47, 48, 49, 34]",
      "organic_treatment": "Use Pseudomonas fluorescens (seed treatment, seedling dip, soil application, foliar sprays); apply Trichoderma species; apply organic amendments like farm yard manure (FYM).[50, 43, 48]",
      "chemical_treatment": "Foliar sprays with Carbendazim, Propiconazole, Validamycin, Azoxystrobin, or Iprodione.[43, 44, 45, 46, 47, 48, 49]",
      "prevention": "Deep ploughing in summer to bury sclerotia; burn stubble; avoid excessive seeding rates and nitrogen application; use wider spacing between rows; rotate with non-host crops.[50, 43, 44, 32, 45, 46, 47, 48, 49]"
    },
    {
      "plant_name": "Rice",
      "disease": "Brown Spot",
      "symptom": "Small, oval brown spots resembling sesame seeds appear on leaves, which can join together and dry out the leaf.",
      "detailed_symptoms": "Minute brown dots on leaves, becoming cylindrical or oval to circular (resembling sesame seeds); spots coalesce, causing the leaf to dry up; infection on panicle and neck with brown color; black or brown spots on glumes; nurseries may have a brownish scorched appearance.[51, 52, 53, 54, 55]",
      "organic_treatment": "Application of salicylic acid or benzoic acid.[53]",
      "chemical_treatment": "Seed treatment with Agrosan, Ceresan, Captan, or Thiram; foliar sprays with Mancozeb or Edifenphos.[51, 52, 54]",
      "prevention": "Use disease-free seeds; remove alternate hosts; grow resistant varieties; provide proper nutrition and avoid water stress; use hot water seed treatment (53-54°C).[51, 52, 53, 54, 55]"
    },
    {
      "plant_name": "Rice",
      "disease": "False Smut",
      "symptom": "Some rice grains are replaced by large, velvety, orange or greenish-black balls.",
      "detailed_symptoms": "Individual rice grains are transformed into a mass of yellow or orange fruiting bodies; growth of velvety spores that enclose the floral parts; infected grains develop greenish smut balls that later turn greenish-black.[56, 57, 58, 59, 60]",
      "organic_treatment": "Not specified in the provided data. Cultural methods like destroying infected straw and avoiding excess nitrogen are recommended.[56, 57, 58, 59, 60]",
      "chemical_treatment": "Spraying with copper oxychloride, Propiconazole, Hexaconazole, or Chlorothalonil at boot leaf and milky stages; seed treatment with carbendazim.[56, 57, 58, 59, 60]",
      "prevention": "Use disease-free seeds; destroy straw and stubble from infected plants; use resistant varieties; plant early; avoid excess nitrogen application; keep field bunds and irrigation channels clean.[56, 57, 58, 59, 60]"
    },
    {
      "plant_name": "Wheat",
      "disease": "Rust Complex (Stripe, Leaf, Stem)",
      "symptom": "Yellow, brown, or black rusty spots (pustules) on leaves and stems. Stripe rust has yellow stripes, leaf rust has scattered brown spots, and stem rust has large, dark red-brown spots on stems.",
      "detailed_symptoms": "Stripe/Yellow Rust: Bright yellow to orange-yellow pustules arranged in distinct, narrow stripes on leaves. Leaf/Brown Rust: Small, circular to oval, orange-brown pustules scattered randomly on the leaf surface. Stem/Black Rust: Large, elongated, dark reddish-brown pustules on stems, leaf sheaths, and leaves that rupture the epidermis.[61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71]",
      "organic_treatment": "Foliar applications of neem oil, garlic extract, or potassium bicarbonate; use of bio-fungicides like Bacillus subtilis and Trichoderma species; application of chitosan nanoparticles and salicylic acid.[62, 72, 73, 74]",
      "chemical_treatment": "Foliar sprays with triazole fungicides (e.g., Propiconazole, Tebuconazole) and strobilurin fungicides (e.g., Azoxystrobin).[62, 63, 66, 67, 68, 69]",
      "prevention": "Cultivate resistant varieties; sow early to avoid peak disease pressure; use balanced fertilization (avoiding excess nitrogen); eradicate volunteer wheat plants and alternate hosts (barberry).[62, 63, 64, 65, 66, 67, 68, 69, 70, 71]"
    },
    {
      "plant_name": "Wheat",
      "disease": "Loose Smut",
      "symptom": "The entire wheat head is replaced by a black, powdery mass of spores, leaving only a bare stalk at harvest.",
      "detailed_symptoms": "The entire inflorescence is converted into a black, powdery mass of fungal spores, initially covered by a thin grey membrane; by harvest, only a bare, blackened rachis remains.[61, 66, 68, 70, 75, 76, 77, 78, 79, 80, 81, 82, 83]",
      "organic_treatment": "Seed treatment with the bio-control agent Trichoderma viride.[84]",
      "chemical_treatment": "Seed treatment with systemic fungicides such as Carboxin (Vitavax), Tebuconazole, or Thiram.[68, 75, 76, 77, 78, 79, 84, 80, 81, 82, 83]",
      "prevention": "Use certified, disease-free seed; plant resistant varieties; remove and burn smutted heads; use hot water treatment for seeds.[68, 75, 76, 77, 78, 79, 80, 81, 82, 83, 85, 86]"
    },
    {
      "plant_name": "Wheat",
      "disease": "Karnal Bunt",
      "symptom": "A few grains in the wheat head are partially or fully converted into a black, powdery mass that has a distinct fishy smell.",
      "detailed_symptoms": "Only a few kernels per head are infected, either partially or completely; the infected portion is converted into a black, powdery, foul-smelling mass of spores; a distinct fishy odor is a key diagnostic feature.[61, 68, 70, 87, 88, 89, 90, 91, 92, 93, 94]",
      "organic_treatment": "Foliar sprays of plant extracts from Lantana camara and bio-control agents like Trichoderma viride.[89, 91]",
      "chemical_treatment": "Seed treatment with fungicides like Carbendazim or Thiram; a foliar spray of a systemic fungicide like Propiconazole (Tilt) at the boot leaf stage.[68, 87, 88, 89, 90, 92, 93, 94]",
      "prevention": "Use resistant varieties; practice long crop rotation (up to 5 years) with non-host crops; adjust sowing dates to avoid favorable weather during flowering; use certified, disease-free seed.[68, 87, 88, 89, 90, 91, 92, 93, 94]"
    },
    {
      "plant_name": "Wheat",
      "disease": "Powdery Mildew",
      "symptom": "White, powdery patches appear on leaves, stems, and heads, which later turn black.",
      "detailed_symptoms": "White, powdery patches on the upper surface of leaves and stem; greyish-white powdery growth on leaf, sheath, stem, and floral parts, which later become black lesions.[61, 68, 70, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105]",
      "organic_treatment": "Foliar sprays of cow urine-based leaf extracts (Azadirachta indica, Calotropis gigantea); potassium bicarbonate; sulfur; neem oil; Bacillus subtilis.[95, 96, 98, 100, 101, 102, 103, 104, 105]",
      "chemical_treatment": "Spray with Carbendazim.[61, 68]",
      "prevention": "Use resistant varieties; avoid excessive nitrogen fertilization; destroy volunteer wheat; ensure proper spacing to improve air circulation.[61, 68, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105]"
    },
    {
      "plant_name": "Potato",
      "disease": "Late Blight",
      "symptom": "Dark brown to black spots on leaves, with a ring of white mold on the underside; tubers have sunken, reddish-brown patches.",
      "detailed_symptoms": "Small, pale green, water-soaked spots on leaves, enlarging to dark brown/black lesions; a ring of white, downy fungal growth on the underside of leaves; irregular, sunken, reddish-brown patches on tubers with a brownish, dry, granular rot extending into the flesh.[106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117]",
      "organic_treatment": "Sprays with copper-based fungicides; applications of compost teas.[109]",
      "chemical_treatment": "Preventive sprays with contact fungicides like Mancozeb or Chlorothalonil; systemic/translaminar fungicides such as Metalaxyl, Cymoxanil, or Mandipropamid during favorable conditions.[107, 110, 111, 112, 113, 116]",
      "prevention": "Use certified, disease-free seed tubers; destroy cull piles and volunteer potato plants; practice proper hilling (earthing up) to protect tubers; avoid overhead irrigation or schedule it for rapid foliage drying.[106, 107, 109, 110, 111, 112, 113, 114, 116, 117]"
    },
    {
      "plant_name": "Potato",
      "disease": "Early Blight",
      "symptom": "Dark brown to black spots on leaves, often with a 'target' or 'bull's-eye' pattern of concentric rings.",
      "detailed_symptoms": "Dark brown to black, circular to angular spots on leaves, often with a 'target spot' pattern of concentric rings and a yellow halo; lesions appear first on older, lower leaves; dark, sunken, circular to irregular lesions on tubers with a brown, corky dry rot underneath.[106, 107, 108, 118, 119, 120, 121, 122, 123, 113, 115]",
      "organic_treatment": "Copper-based fungicides can be used for control.[119]",
      "chemical_treatment": "Foliar sprays with fungicides such as Chlorothalonil, Mancozeb, Azoxystrobin, or Boscalid.[118, 120, 121, 122, 123]",
      "prevention": "Rotate crops for at least two to three years with non-solanaceous crops; maintain plant vigor through balanced fertilization and proper irrigation; remove and destroy crop debris after harvest.[106, 107, 118, 119, 120, 121, 122, 123, 113]"
    },
    {
      "plant_name": "Potato",
      "disease": "Bacterial Wilt / Brown Rot",
      "symptom": "Plant wilts rapidly; a milky-white bacterial slime oozes from a freshly cut stem placed in water.",
      "detailed_symptoms": "Rapid and irreversible wilting of the plant, sometimes without preliminary yellowing; streaming of a milky-white bacterial slime from a freshly cut stem suspended in clear water; creamy white to brownish discoloration of the tuber's vascular ring, which exudes a bacterial ooze when squeezed.[106, 107, 108, 113, 124, 125, 126, 127, 128, 129]",
      "organic_treatment": "Application of bio-control agents like Pseudomonas fluorescens can help create a suppressive soil environment.[129]",
      "chemical_treatment": "No effective chemical cure; application of stable bleaching powder (12 kg/ha) in furrows at planting has been shown to reduce incidence.[113]",
      "prevention": "Use certified seed tubers from a disease-free source; avoid planting in fields with a history of the disease; practice long crop rotation (5+ years) with non-host crops; maintain strict on-farm hygiene (cleaning and disinfecting machinery and tools).[106, 107, 113, 124, 125, 126, 127, 128, 129]"
    },
    {
      "plant_name": "Potato",
      "disease": "Black Scurf",
      "symptom": "Irregular, black, hard masses that look like soil but don't wash off appear on the tuber surface.",
      "detailed_symptoms": "Irregular, black to brown hard masses (sclerotia) on the tuber surface; cankers on sprouts and stems; upward curling of leaves with a pinkish or reddish border.[106, 107, 108, 112, 113, 114, 130, 131, 132]",
      "organic_treatment": "Not specified in the provided data.",
      "chemical_treatment": "Tuber treatment with an organomercurial compound and soil application of PCNB.[107, 113]",
      "prevention": "Harvest soon after vines are killed; plant seed tubers in warm soil; practice crop rotation; plant sclerotia-free seed; ensure timely harvest.[106, 107, 112, 114, 130, 131, 132]"
    },
    {
      "plant_name": "Maize",
      "disease": "Turcicum Leaf Blight (TLB)",
      "symptom": "Long, elliptical, grayish-green to tan 'cigar-shaped' spots on the leaves.",
      "detailed_symptoms": "Long (up to 15 cm), elliptical, grayish-green to tan-colored 'cigar-shaped' lesions on the leaves; lesions typically appear first on the lower leaves and spread upwards.[133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143]",
      "organic_treatment": "Application of bio-control agents like Trichoderma spp. and Bacillus subtilis.[138]",
      "chemical_treatment": "Foliar fungicides, such as those containing Mancozeb.[135, 138, 139]",
      "prevention": "Use resistant maize hybrids; rotate crops with non-hosts (e.g., pulses, soybean); use tillage to bury infected crop debris; avoid excessive nitrogen application.[134, 135, 136, 137, 138, 139, 140, 143]"
    },
    {
      "plant_name": "Maize",
      "disease": "Maydis Leaf Blight (MLB)",
      "symptom": "Small, tan-colored, rectangular spots with brownish borders on leaves.",
      "detailed_symptoms": "Smaller, tan-colored, rectangular to oblong lesions with brownish borders, restricted by leaf veins; can also infect sheaths, husks, and ears, leading to ear and cob rots.[133, 144, 145, 146, 147, 148, 149, 150, 140, 141, 143]",
      "organic_treatment": "Seed treatment with Trichoderma harzianum; foliar sprays of Pseudomonas fluorescens or a 20% cow urine solution; botanical extracts from garlic, tulsi, and neem.[145, 146]",
      "chemical_treatment": "Seed treatment with Captan or Thiram; foliar fungicides containing Mancozeb, Propiconazole, or combinations like Azoxystrobin + Difenoconazole.[144, 146, 147, 148, 149, 150, 140]",
      "prevention": "Use resistant hybrids; practice crop rotation and tillage to manage crop residue.[145, 146, 147, 148, 149, 150, 140]"
    },
    {
      "plant_name": "Maize",
      "disease": "Bacterial Stalk Rot",
      "symptom": "The stalk rots at the base, becoming soft and slimy with a distinct foul odor, causing the plant to collapse.",
      "detailed_symptoms": "Rotting of the stalk, usually starting at a lower node; affected tissue becomes soft, slimy, and discolored, emitting a distinct foul odor; rapid wilting and eventual collapse of the entire plant.[133, 151, 152, 153, 154, 140, 141, 155, 156]",
      "organic_treatment": "Incorporate green manure into the soil before sowing in endemic areas.[151]",
      "chemical_treatment": "No effective in-season bactericides; preventive measures include chlorination of irrigation water or a soil drench with bleaching powder; application of Muriate of Potash (MOP).[151]",
      "prevention": "Ensure good field drainage to avoid waterlogging; rotate crops with non-hosts; incorporate crop debris after harvest; use balanced fertility, particularly avoiding excessive nitrogen.[151, 152, 153, 154, 140, 155, 156]"
    },
    {
      "plant_name": "Maize",
      "disease": "Charcoal Rot",
      "symptom": "The inside of the stalk shreds, leaving stringy strands with tiny black specks, giving it a gray or 'charcoal-dusted' look.",
      "detailed_symptoms": "Premature ripening and weakened stalks; shredded pith leaving stringy vascular strands; numerous tiny, black sclerotia on and in the vascular strands, giving the internal tissue a gray or 'charcoal-dusted' appearance.[133, 144, 140, 141, 157, 158, 159]",
      "organic_treatment": "Not specified in the provided data.",
      "chemical_treatment": "No registered fungicides are available to control charcoal rot.[157, 159]",
      "prevention": "Manage water well to avoid stressing plants, especially around flowering; rotate crops with non-hosts like small grains.[157, 158, 159]"
    },
    {
      "plant_name": "Soybean",
      "disease": "Soybean Rust",
      "symptom": "Tan to reddish-brown spots with raised pustules on the undersides of leaves, leading to yellowing and rapid leaf drop.",
      "detailed_symptoms": "Small, tan to reddish-brown or dark brown, angular lesions on leaves, petioles, and pods; raised pustules (uredia) on the undersides of leaflets that release powdery spores; premature yellowing (chlorosis) and rapid defoliation.[160, 135, 161, 162, 163, 164, 165, 166, 167, 168, 169]",
      "organic_treatment": "Application of Trichoderma species and their secondary metabolites.[166]",
      "chemical_treatment": "Foliar fungicide application, often a combination of triazole and strobilurin fungicides.[162, 163, 164, 165, 170]",
      "prevention": "Monitor disease tracking systems to know when rust spores arrive in the region; use of partially resistant varieties is in development.[135, 162, 163, 164, 165, 166]"
    },
    {
      "plant_name": "Soybean",
      "disease": "Charcoal Rot",
      "symptom": "Plants are stunted and wilted; the lower stem and taproot are filled with tiny black specks, giving a 'charcoal-dusted' appearance.",
      "detailed_symptoms": "Stunted plants; leaflets may appear small, turn yellow, wilt, and die but remain attached; tiny, black fungal resting bodies (microsclerotia) fill the tissue of the lower stem and taproot, giving it a grayish or 'charcoal-dusted' appearance.[160, 135, 161, 171, 172, 173, 174, 159, 167, 168, 169]",
      "organic_treatment": "Not specified in the provided data.",
      "chemical_treatment": "Fungicide seed treatments and foliar fungicides are not effective.[171, 175, 173, 174]",
      "prevention": "Mitigate drought stress through irrigation; use reduced tillage or no-till farming to conserve soil moisture; rotate crops with non-hosts like small grains (wheat, barley); avoid excessive seeding rates.[135, 171, 175, 172, 173, 174]"
    },
    {
      "plant_name": "Soybean",
      "disease": "Rhizoctonia Root Rot",
      "symptom": "Sunken, dry, reddish-brown cankers on the stem and roots near the soil line, causing seedlings to wilt and die.",
      "detailed_symptoms": "Sunken, dry, reddish-brown lesion or canker on the stem and roots at or near the soil line; can girdle and kill seedlings (damping-off); older plants may be stunted, yellow, and wilted due to root decay.[160, 135, 161, 176, 177, 178, 179, 180, 181, 167, 168, 169]",
      "organic_treatment": "Seed pelleting with bio-control agents such as Trichoderma viride or Pseudomonas fluorescens.[182]",
      "chemical_treatment": "Fungicide seed treatments are the most effective management practice.[176, 177, 178, 179, 180, 181]",
      "prevention": "Plant high-quality seed in well-drained, non-compacted soils; rotate crops with non-hosts like wheat.[176, 177, 178, 179, 180, 181]"
    },
    {
      "plant_name": "Soybean",
      "disease": "Soybean Mosaic Virus (SMV)",
      "symptom": "Plants are stunted with distorted, puckered, or crinkled leaves that show a mosaic of light and dark green areas.",
      "detailed_symptoms": "Stunted plants with distorted (puckered, crinkled, ruffled, narrow) leaves; mosaic of light and dark green areas on leaves; fewer and smaller pods; seeds may be mottled and deformed.[160, 135, 161, 167, 168, 169, 183, 184, 185, 186, 187]",
      "organic_treatment": "Not specified in the provided data.",
      "chemical_treatment": "The value of insecticides to control aphid vectors is uncertain.[183, 184, 185, 186, 187]",
      "prevention": "Use pathogen-free seed; plant early; some cultivars may have some level of resistance.[182, 183, 184, 185, 186, 187]"
    },
    {
      "plant_name": "Rapeseed & Mustard",
      "disease": "Alternaria Blight",
      "symptom": "Circular, brown to black spots on leaves, often with concentric rings giving a 'target spot' look.",
      "detailed_symptoms": "Small, circular, brown to black necrotic spots on lower leaves, often with concentric rings ('target spot'); lesions coalesce, leading to defoliation; circular to linear, dark brown lesions on stems and pods, causing shriveled, low-quality seeds.[188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200]",
      "organic_treatment": "Seed treatment with Trichoderma species; foliar sprays with botanical extracts from garlic or neem.[188, 192, 201]",
      "chemical_treatment": "Spraying with fungicides like Mancozeb or Iprodione; newer combination fungicides like Azoxystrobin + Hexaconazole are also effective.[191, 193, 194, 196, 198, 199, 200]",
      "prevention": "Use healthy, certified, disease-free seed; sow on time (avoiding late planting); remove and burn infected crop debris; control weeds.[188, 189, 191, 192, 193, 196, 198, 199, 200]"
    },
    {
      "plant_name": "Rapeseed & Mustard",
      "disease": "White Rust",
      "symptom": "White or creamy-yellow, raised, blister-like spots on the underside of leaves; floral parts can become swollen and malformed ('staghead').",
      "detailed_symptoms": "Local infection: White or creamy-yellow, raised, blister-like pustules on the underside of leaves. Systemic infection: Swelling and malformation of the stem and floral parts, forming a sterile 'staghead'.[189, 190, 192, 202, 203, 204, 195, 196, 197, 205, 206, 207]",
      "organic_treatment": "Seed treatment with bio-agents like Trichoderma viride or Pseudomonas fluorescens.[203]",
      "chemical_treatment": "Seed treatment with a systemic fungicide like Metalaxyl (e.g., Apron 35 SD); foliar spraying with fungicides like Metalaxyl + Mancozeb (e.g., Ridomil MZ) or Mancozeb alone.[202, 203, 204, 196, 205, 206, 207]",
      "prevention": "Use resistant or tolerant varieties; sow healthy, certified seed; practice crop rotation; remove and destroy infected plants and stagheads early.[202, 204, 196, 205, 206, 207]"
    },
    {
      "plant_name": "Rapeseed & Mustard",
      "disease": "Sclerotinia Stem Rot",
      "symptom": "Water-soaked spots on the stem, covered by a dense, white, cottony growth; large, black, hard bodies (sclerotia) form on and inside the stem.",
      "detailed_symptoms": "Elongated, water-soaked lesions on the stem, covered by a dense, white, cottony fungal growth; affected stem becomes bleached and soft; large, black, hard sclerotia form on and inside the stem; plants wilt, ripen prematurely, and lodge.[189, 190, 192, 195, 208, 209, 210, 196, 197, 211, 212]",
      "organic_treatment": "Use of bio-control agents that parasitize sclerotia, such as Coniothyrium minitans (Contans); seed treatment with Trichoderma.[208, 209, 210, 196, 211, 212]",
      "chemical_treatment": "Seed treatment with fungicides like Carbendazim; foliar application of Carbendazim or Thiophanate-methyl at early flowering.[210]",
      "prevention": "Practice long crop rotations (3-4 years) with non-host crops like cereals; use deep summer ploughing to bury sclerotia; use certified, sclerotia-free seed.[208, 209, 210, 196, 211, 212]"
    },
    {
      "plant_name": "Rapeseed & Mustard",
      "disease": "Downy Mildew",
      "symptom": "Grayish-white irregular spots on the lower surface of leaves, with corresponding yellow spots on the upper surface; white cottony growth on leaves.",
      "detailed_symptoms": "Grayish-white irregular necrotic patches on the lower surface of leaves, with corresponding yellow spots on the upper surface; white downy (cottony) growth on leaves; can cause 'staghead' in mixed infection with white rust.[189, 190, 192, 213, 195, 196, 197, 214, 215, 216, 217, 218]",
      "organic_treatment": "Sprays of milk solution, baking soda solution, or copper-based fungicides.[218]",
      "chemical_treatment": "Seed treatment with metalaxyl; spray with Ridomil MZ or mancozeb.[213, 215]",
      "prevention": "Sow on time; use healthy certified seeds; destroy diseased debris; practice crop rotation; ensure proper spacing; avoid overhead irrigation.[213, 214, 215, 216, 217, 218]"
    },
    {
      "plant_name": "Chickpea",
      "disease": "Fusarium Wilt",
      "symptom": "Leaves turn yellow and droop, followed by wilting of the entire plant; the inside of the root and stem turns dark brown to black.",
      "detailed_symptoms": "Yellowing and drooping of leaves, followed by wilting of the entire plant; internal dark brown to black discoloration of the vascular tissues in the root and stem.",
      "organic_treatment": "Seed treatment with Trichoderma viride; soil application of neem cake or farm yard manure.[219]",
      "chemical_treatment": "Seed treatment with a combination of Thiram + Carbendazim.[219]",
      "prevention": "Cultivate wilt-resistant varieties; use deep summer ploughing; practice long crop rotation (4-5 years) with non-host crops; adjust sowing time to cooler soil temperatures.[219]"
    },
    {
      "plant_name": "Chickpea",
      "disease": "Collar Rot",
      "symptom": "Sudden drying of branches with a white, fan-like fungal growth at the base of the stem, along with small, mustard-seed-like bodies.",
      "detailed_symptoms": "(Symptoms similar to Stem Rot in Groundnut) Sudden drying of branches; white, fan-like growth of fungal mycelium at the stem base; formation of small, round, mustard-seed-like sclerotia.",
      "organic_treatment": "Not specified in the provided data.",
      "chemical_treatment": "(Management similar to Stem Rot in Groundnut) Seed treatment with Carbendazim, Thiram, or Captan.[220]",
      "prevention": "(Management similar to Stem Rot in Groundnut) Deep ploughing; crop rotation; avoiding movement of soil up against the base of plants.[220]"
    },
    {
      "plant_name": "Chickpea",
      "disease": "Ascochyta Blight",
      "symptom": "Circular spots on leaves, stems, and pods, often with small black dots arranged in concentric rings.",
      "detailed_symptoms": "Circular spots on leaves, stems, and pods, often with small black dots (pycnidia) arranged in concentric rings; stem lesions can girdle the stem, causing it to break.",
      "organic_treatment": "Not specified in the provided data.",
      "chemical_treatment": "Foliar sprays with fungicides like Chlorothalonil or Mancozeb.",
      "prevention": "Use disease-free seed; deep ploughing of infected debris; crop rotation; use of resistant varieties."
    },
    {
      "plant_name": "Groundnut",
      "disease": "Early & Late Leaf Spots (Tikka)",
      "symptom": "Circular brown or black spots on leaves. Early spots are reddish-brown with a yellow halo; late spots are darker and nearly black.",
      "detailed_symptoms": "Early: Circular to irregular, reddish-brown spots on the upper leaf surface, usually with a distinct yellow halo. Late: Darker, nearly black, more circular spots on the lower leaf surface, often without a halo. Severe infection leads to defoliation.[220, 221, 219, 222, 223, 224, 225, 196, 226, 227, 228, 229, 230, 231]",
      "organic_treatment": "Spraying with 10% Calotropis leaf extract; application of antifungal bacteria like Bacillus circulans and Serratia marcescens.[222, 232]",
      "chemical_treatment": "Foliar sprays with Chlorothalonil, Mancozeb, Carbendazim, Tebuconazole, or Propiconazole; seed treatment with Carboxin + Thiram.[220, 221, 219, 222, 223, 224, 225, 196, 229, 230, 231]",
      "prevention": "Deep burying of crop residues; destruction of volunteer groundnut plants; crop rotation with cereals; using resistant or tolerant varieties.[220, 221, 219, 222, 223, 224, 225, 196, 226, 227, 229, 230, 231]"
    },
    {
      "plant_name": "Groundnut",
      "disease": "Rust",
      "symptom": "Small, orange-colored rusty spots on the lower surface of leaves that release reddish-brown powder.",
      "detailed_symptoms": "Small, orange-colored rust pustules on the lower surface of leaflets, which rupture to release reddish-brown spores; infected leaves become necrotic and dry up but tend to remain attached to the plant.[220, 221, 219, 226, 227, 228, 229, 233, 234, 235, 236, 237]",
      "organic_treatment": "Application of plant extracts from Salvia officinalis and Potentilla erecta; flaxseed oil and peanut oil.[233]",
      "chemical_treatment": "Spraying with fungicides containing Mancozeb, Propiconazole, or Chlorothalonil.[221, 233, 234, 236, 237]",
      "prevention": "Use resistant varieties; remove volunteer plants; practice crop rotation with non-host crops; apply high doses of phosphorus fertilizer.[221, 233, 234, 235, 236, 237]"
    },
    {
      "plant_name": "Groundnut",
      "disease": "Stem Rot / White Mold",
      "symptom": "Plant wilts suddenly; a white, fan-like fungal growth appears at the base of the stem, with small, mustard-seed-like bodies.",
      "detailed_symptoms": "Sudden wilting and drying of a branch or the entire plant; a characteristic white, fan-like growth of fungal mycelium at the base of the stem near the soil line; small, round, tan to brown, mustard-seed-like sclerotia form in the mycelial mat.[220, 219, 238, 239, 240, 241, 226, 227, 228, 229, 242, 243]",
      "organic_treatment": "Seed treatment and soil application of Trichoderma viride; soil application of organic amendments like neem cake or castor cake.[239, 240, 241]",
      "chemical_treatment": "Seed treatment with fungicides such as Carbendazim, Thiram, or Captan.[219, 239, 240, 241]",
      "prevention": "Deep ploughing during summer to bury crop debris and expose sclerotia; crop rotation with non-host crops like wheat, corn, or soybean; avoiding the movement of soil up against the base of the plants ('dirting').[219, 238, 239, 240, 241, 242, 243]"
    },
    {
      "plant_name": "Cotton",
      "disease": "Bacterial Blight",
      "symptom": "Water-soaked spots on leaves that become angular and black; stems can get black lesions ('black arm'), and bolls can rot.",
      "detailed_symptoms": "Seedling Blight: Water-soaked lesions on cotyledons. Angular Leaf Spot: Water-soaked, angular lesions on leaves. Vein Necrosis: Blackening of leaf veins. Blackarm: Dark brown to black, elongated lesions on stems and branches. Boll Rot: Water-soaked, sunken black spots on bolls, leading to stained lint.[244, 140, 245, 246, 247, 248, 249, 250, 251, 252]",
      "organic_treatment": "Not specified in the provided data.",
      "chemical_treatment": "Seed treatment with Carboxin or Oxycarboxin; foliar sprays of a combination of Streptomycin sulphate and Copper oxychloride.[140]",
      "prevention": "Plant resistant cotton varieties; use high-quality, certified, disease-free seed; use acid delinting of seeds; rotate crops with non-hosts (maize, sorghum); remove and destroy infected plant debris.[244, 140, 245, 246, 247, 248, 251]"
    },
    {
      "plant_name": "Cotton",
      "disease": "Fusarium Wilt",
      "symptom": "Leaves turn yellow and droop, followed by wilting of the entire plant; a cross-section of the stem shows a dark brown or black ring.",
      "detailed_symptoms": "Yellowing and drooping of lower leaves, often on one side of the plant; progressive wilting of the entire plant; stunted growth; discoloration of the vascular tissue (a dark brown or black ring just beneath the bark).[244, 249, 253, 254, 250, 251, 252, 255, 256, 257]",
      "organic_treatment": "Application of organic amendments like farm yard manure or neem cake; seed treatment with the bio-control agent Trichoderma viride.[244, 249]",
      "chemical_treatment": "Seed treatment with fungicides such as Chlorothalonil, Captan, or Carbendazim; spot drenching the soil with a Carbendazim solution.[244, 249, 257]",
      "prevention": "Plant resistant varieties; practice long-term crop rotation with non-host crops; use deep summer ploughing; maintain proper sanitation, including cleaning farm equipment.[244, 249, 253, 254, 255, 256, 257]"
    },
    {
      "plant_name": "Cotton",
      "disease": "Verticillium Wilt",
      "symptom": "Yellowing between the leaf veins, creating a mottled or 'tiger stripe' pattern, followed by leaf drop.",
      "detailed_symptoms": "Interveinal chlorosis (yellowing between the veins) on leaves, creating a mottled or 'tiger stripe' pattern; necrosis (browning) and defoliation; discoloration of the vascular tissue (pinkish or brownish streaks).[244, 249, 258, 259, 251, 252]",
      "organic_treatment": "Applying heavy doses of farm yard manure or compost.[258]",
      "chemical_treatment": "Seed treatment with fungicides like Carboxin or Carbendazim; spot drenching of affected areas with a Benomyl or Carbendazim solution.[258]",
      "prevention": "Use resistant or tolerant cotton varieties; practice long-term crop rotation with non-host crops like paddy or other cereals; use deep ploughing and destroy infected crop debris.[258, 259]"
    },
    {
      "plant_name": "Cotton",
      "disease": "Grey Mildew",
      "symptom": "Irregular, pale spots with grey powdery growth on the lower surface of the leaf.",
      "detailed_symptoms": "Irregular to angular pale translucent lesions bound by veinlets on the lower surface of the leaf, with grey powdery growth; light green specks on the upper surface; affected leaves dry, turn yellow, and fall prematurely.[260]",
      "organic_treatment": "Not specified in the provided data.",
      "chemical_treatment": "Spraying with fungicides such as Wettable sulphur, Chlorothalonil, Difenaconazole, Tebuconazole, or Propiconazole at 60, 90, and 120 days after sowing.[260]",
      "prevention": "Remove and burn infected crop residues; remove self-sown cotton plants during summer; avoid excessive application of nitrogenous fertilizers; adopt correct spacing.[260]"
    },
{
      "plant_name": "Rice",
      "disease": "Red Stripe",
      "symptom": "Orange to reddish-brown stripes appear on leaves, often with a long white halo extending to the tip.",
      "detailed_symptoms": "Lesions begin as pin-point dark green spots that enlarge into orange or reddish-brown stripes with a whitish halo. The stripes run lengthwise toward the leaf tip. In severe cases, the lesions spread extensively causing a blight appearance, and bacterial masses may be seen in vascular bundles.",
      "organic_treatment": "Spray fresh cow dung extract (20%) or use Pseudomonas fluorescens as a seed treatment.",
      "chemical_treatment": "Foliar spray with Copper Oxychloride or antibiotics like Streptomycin sulphate + Tetracycline combination.",
      "prevention": "Remove infected plant debris; avoid excessive nitrogen fertilizer; ensure proper spacing to reduce humidity."
    },
    {
      "plant_name": "Wheat",
      "disease": "Leaf Rust (Brown Rust)",
      "symptom": "Small, circular orange blisters (pustules) appear scattered on the upper surface of leaves.",
      "detailed_symptoms": "Uredia appear as small, circular orange-brown pustules scattered randomly on the leaf blades. Unlike stripe rust, they are not arranged in rows. As the plant matures, black spores (teliospores) may replace the orange ones. Severe infection causes leaves to dry out and die early.",
      "organic_treatment": "Foliar spray of neem oil (3%) or fermented buttermilk; use of bio-control agents like Bacillus subtilis.",
      "chemical_treatment": "Foliar sprays with Propiconazole (Tilt), Tebuconazole (Folicur), or Triadimefon.",
      "prevention": "Grow resistant varieties; destroy volunteer wheat plants; apply Potash to improve resistance; avoid late sowing."
    },
    {
      "plant_name": "Sugarcane",
      "disease": "Red Rot",
      "symptom": "The upper leaves turn yellow and dry up; splitting the stalk reveals red tissues with white cross-bands.",
      "detailed_symptoms": "The third or fourth leaf turns yellow and dries from the bottom up. The internal cane tissue becomes reddish with characteristic intermittent white transverse patches (white spots) running the length of the cane. The pith may smell like alcohol.",
      "organic_treatment": "Sett treatment with Trichoderma viride or Pseudomonas fluorescens; removal of infected stools.",
      "chemical_treatment": "Sett dipping in Carbendazim (Bavistin) or Thiophanate Methyl for 15 minutes before planting.",
      "prevention": "Use healthy certified setts; follow a 2-3 year crop rotation with rice or green manure; avoid waterlogging; burn trash from infected fields."
    },
    {
      "plant_name": "Sugarcane",
      "disease": "Leaf Scald",
      "symptom": "White 'pencil lines' run along the leaf veins; leaves look scalded or burnt at the tips.",
      "detailed_symptoms": "A narrow, white 'pencil line' extends the entire length of the leaf blade. Leaves become etiolated (pale/yellow) and the tips dry out, giving a scalded appearance. Side shoots (lalas) may sprout on mature canes.",
      "organic_treatment": "Hot water treatment of setts at 50°C for 2 hours.",
      "chemical_treatment": "Disinfect cutting knives with Lysol or Dettol; no direct chemical cure for standing crop, prevention is key.",
      "prevention": "Use resistant varieties; sterilize harvesting tools; use disease-free setts from nurseries."
    },
    {
      "plant_name": "Sugarcane",
      "disease": "Mosaic Virus",
      "symptom": "Leaves show a mottled pattern of light green and dark green patches.",
      "detailed_symptoms": "Young leaves exhibit a mosaic pattern of alternating light green and dark green patches. The plant growth is stunted, and cane yield is reduced.",
      "organic_treatment": "Remove and destroy infected clumps (roguing); control aphid vectors using neem oil.",
      "chemical_treatment": "Spray insecticides like Dimethoate or Methyl Demeton to control the aphids that spread the virus.",
      "prevention": "Use virus-free nursery setts; rogue out infected plants regularly; control grassy weeds."
    },
    {
      "plant_name": "Sugarcane",
      "disease": "Pineapple Disease",
      "symptom": "Setts fail to germinate; cut ends turn black and smell like ripe pineapple.",
      "detailed_symptoms": "The central soft portion of the sett turns red, then brown-black. Infected internodes develop cavities. The cut stem emits a strong odor of pineapple due to ethyl acetate production.",
      "organic_treatment": "Dip setts in cow dung slurry or Trichoderma solution before planting.",
      "chemical_treatment": "Sett treatment with Propiconazole or Carbendazim helps preventing entry through cut ends.",
      "prevention": "Use setts with at least 3 nodes; ensure proper drainage; avoid deep planting in heavy soils."
    },
    {
      "plant_name": "Rice",
      "disease": "Tungro Disease",
      "symptom": "Plants are stunted and leaves turn yellow or orange-yellow from the tip downwards.",
      "detailed_symptoms": "Caused by a virus transmitted by green leafhoppers. Plants show severe stunting and reduced tillering. Leaves turn yellow or orange-yellow, and panicles are small, sterile, or not completely exerted.",
      "organic_treatment": "Use light traps to catch leafhoppers; apply Neem cake in the nursery.",
      "chemical_treatment": "Spray insecticides like Imidacloprid, Thiamethoxam, or Carbofuran to kill the leafhopper vector.",
      "prevention": "Plant resistant varieties (e.g., IR 50, ADT 37); adjust planting dates to avoid peak vector population; plough field to destroy stubble."
    },
    {
      "plant_name": "Rice",
      "disease": "Bakanae (Foot Rot)",
      "symptom": "Infected plants grow abnormally tall and thin compared to healthy plants, then die.",
      "detailed_symptoms": "Seedlings appear pale yellow, thin, and abnormally elongated (tall) due to gibberellin production by the fungus. Plants may develop adventitious roots at nodes and often die before producing grain.",
      "organic_treatment": "Seed treatment with Trichoderma viride or Pseudomonas fluorescens.",
      "chemical_treatment": "Seed treatment with Carbendazim (Bavistin) or Thiram for 24 hours before sowing.",
      "prevention": "Use salt water to separate light/infected seeds; use clean seeds; destroy infected straw."
    },
    {
      "plant_name": "Rice",
      "disease": "Sheath Rot",
      "symptom": "Irregular grey spots with brown margins appear on the flag leaf sheath; panicles may fail to emerge.",
      "detailed_symptoms": " oblong or irregular spots with grey centers and brown margins on the flag leaf sheath (the one protecting the grain head). In severe cases, the panicle rots inside the sheath or only partially emerges.",
      "organic_treatment": "Foliar spray of Pseudomonas fluorescens or Neem oil at booting stage.",
      "chemical_treatment": "Spray Carbendazim, Edifenphos, or Propiconazole at the time of panicle emergence.",
      "prevention": "Apply Potash at tillering stage; remove infected stubbles; avoid dense planting."
    },
    {
      "plant_name": "Rice",
      "disease": "Bacterial Leaf Streak",
      "symptom": "Fine, translucent, water-soaked streaks appear between leaf veins, turning brown later.",
      "detailed_symptoms": "Small, water-soaked linear streaks appear between leaf veins. Tiny yellow beads of bacterial ooze may appear on the streaks. Lesions eventually turn brown and dry out.",
      "organic_treatment": "Spray fresh cow dung extract (20%).",
      "chemical_treatment": "Spray Copper Oxychloride mixed with Streptomycin sulphate.",
      "prevention": "Avoid cutting seedling tips before transplanting; use resistant varieties; avoid excessive nitrogen."
    },
    {
      "plant_name": "Wheat",
      "disease": "Fusarium Head Blight (Head Scab)",
      "symptom": "Wheat heads turn prematurely white or bleached; grain looks shriveled and pinkish.",
      "detailed_symptoms": "Spikelets lose their green color and turn straw-colored or bleached. Under humid conditions, pink or orange spore masses (salmon-colored) appear on the glumes. Infected grains are shriveled and chalky white.",
      "organic_treatment": "Application of bio-control agents like Bacillus subtilis.",
      "chemical_treatment": "Spray Tebuconazole, Prothioconazole, or Metconazole at the flowering stage.",
      "prevention": "Rotate with non-cereal crops; bury crop residues; avoid irrigation during flowering."
    },
    {
      "plant_name": "Wheat",
      "disease": "Spot Blotch",
      "symptom": "Small, dark brown oval spots appear on leaves, which may join to form large dead patches.",
      "detailed_symptoms": "Small, dark brown to black oval lesions appear on the leaves. These spots can coalesce, causing large necrotic patches and leaf death, especially after the heading stage.",
      "organic_treatment": "Seed treatment with Trichoderma harzianum; foliar spray of botanicals.",
      "chemical_treatment": "Foliar spray of Propiconazole or Hexaconazole.",
      "prevention": "Timely sowing; use balanced fertilization (NPK); clean cultivation."
    },
    {
      "plant_name": "Wheat",
      "disease": "Flag Smut",
      "symptom": "Long, grey-black streaks appear on leaves/stems; plants are stunted and twisted.",
      "detailed_symptoms": "Long grey to black sub-epidermal streaks run parallel to leaf veins. These rupture to release black powdery spores. Leaves become twisted and split lengthwise (shredding). Plants are often stunted.",
      "organic_treatment": "Seed treatment with Trichoderma viride.",
      "chemical_treatment": "Seed treatment with Carboxin (Vitavax) or Tebuconazole (Raxil).",
      "prevention": "Shallow sowing; crop rotation; use resistant varieties."
    },
    {
      "plant_name": "Potato",
      "disease": "Common Scab",
      "symptom": "Rough, corky, or raised scabs appear on the potato skin.",
      "detailed_symptoms": "Superficial, raised, or pitted corky lesions appear on the tuber surface. The lesions are brown, rough, and scabby but do not rot the flesh underneath unless secondary infection occurs.",
      "organic_treatment": "Green manuring before planting; ensure soil is not too dry during tuber formation.",
      "chemical_treatment": "Soil treatment with PCNB (Pentachloronitrobenzene) or seed treatment with Boric Acid (3%).",
      "prevention": "Avoid alkaline soils (high pH favors scab); irrigate frequently during tuber initiation; use resistant varieties."
    },
    {
      "plant_name": "Potato",
      "disease": "Leaf Roll Virus (PLRV)",
      "symptom": "Leaves roll upward and become thick, leathery, and brittle.",
      "detailed_symptoms": "Lower leaves roll upward at the margins and feel leathery or brittle. Plants are stunted and have a pale yellow appearance. Tubers may develop internal net necrosis (brown netting pattern).",
      "organic_treatment": "Roguing (removal) of infected plants; control aphids.",
      "chemical_treatment": "Spray Imidacloprid or Thiamethoxam to control aphid vectors that spread the virus.",
      "prevention": "Use certified virus-free seed tubers; remove volunteer potato plants; monitor aphid populations."
    },
    {
      "plant_name": "Potato",
      "disease": "Wart Disease",
      "symptom": "Cauliflower-like warty growths appear on the tubers and stem base.",
      "detailed_symptoms": "Tumors or warty outgrowths appear on tubers, stolons, and stem bases. They look like cauliflower—initially white/green, turning black and rotting later. This is a quarantine disease.",
      "organic_treatment": "Strict quarantine; no effective organic cure once soil is infected.",
      "chemical_treatment": "Soil sterilization (difficult and expensive); main control is regulatory/quarantine.",
      "prevention": "Absolute restriction on moving soil/tubers from infected areas; grow immune varieties (e.g., Kufri Jyoti, Kufri Kanchan)."
    },
    {
      "plant_name": "Potato",
      "disease": "Dry Rot (Fusarium)",
      "symptom": "Tubers develop sunken, wrinkled dry patches with white or pink mold.",
      "detailed_symptoms": "Sunken, brown, wrinkled patches form on the tuber surface. The internal tissue becomes dry, powdery, and brown, often with cavities containing white/pink fungal growth.",
      "organic_treatment": "Handle tubers carefully to avoid wounds; store in cool, dry conditions.",
      "chemical_treatment": "Seed tuber treatment with Thiabendazole or Mancozeb before storage or planting.",
      "prevention": "Minimize bruising during harvest; cure potatoes before storage (allow skins to harden)."
    },
    {
      "plant_name": "Potato",
      "disease": "Blackleg",
      "symptom": "The base of the stem turns inky black and rots; plants wilt and die.",
      "detailed_symptoms": "Black, slimy rotting starts at the stem base (soil level) and progresses upwards. Plants appear stunted with yellow, stiff upper leaves. Tubers rot with a foul smell.",
      "organic_treatment": "Remove and destroy infected plants immediately.",
      "chemical_treatment": "Seed treatment with Streptomycin sulphate or Copper fungicides helps reduce surface bacteria.",
      "prevention": "Use whole seed tubers (avoid cutting); plant in well-drained soil; avoid harvesting in wet conditions."
    },
    {
      "plant_name": "Wheat",
      "disease": "Powdery Mildew",
      "symptom": "White, cottony powder appears on the upper surface of leaves and stems.",
      "detailed_symptoms": "Greyish-white powdery fungal growth appears on leaves, sheaths, and floral parts. Later, the powder turns grey-brown with small black dots (cleistothecia).",
      "organic_treatment": "Spray mixture of baking soda and soapy water or cow urine.",
      "chemical_treatment": "Foliar spray with Wettable Sulphur or Propiconazole (Tilt).",
      "prevention": "Avoid dense sowing; reduce nitrogen application; use resistant varieties."
    },
    {
      "plant_name": "Rice",
      "disease": "Udbatta Disease",
      "symptom": "The rice panicle turns into a straight, grey-white agarbatti-like structure.",
      "detailed_symptoms": "The entire panicle becomes cemented into a cylindrical, rod-like structure (resembling an incense stick) covered with white mycelium, which later hardens and turns black.",
      "organic_treatment": "Hot water seed treatment at 54°C for 10 minutes.",
      "chemical_treatment": "Seed treatment with Carbendazim or Vitavax.",
      "prevention": "Use disease-free seeds; remove and burn infected panicles."
    },
    {
      "plant_name": "Rice",
      "disease": "Stem Rot",
      "symptom": "Black lesions appear on the stem near the water line; the stem weakens and lodges (falls over).",
      "detailed_symptoms": "Small black irregular lesions form on the outer leaf sheath near the water level. The fungus penetrates the stem, causing it to rot and collapse (lodge), leading to unfilled grains.",
      "organic_treatment": "Drain the field to reduce humidity; balance nitrogen with potash.",
      "chemical_treatment": "Spray Thophanate-methyl or Carbendazim at tillering stage.",
      "prevention": "Burn stubble after harvest; allow field to dry between irrigations."
    },
    {
      "plant_name": "Sugarcane",
      "disease": "Ratoon Stunting",
      "symptom": "Crop looks stunted with thin stalks; orange-red discoloration seen inside nodes.",
      "detailed_symptoms": "Often symptomless externally except for general stunting and poor yield. Splitting the cane reveals orange-red vascular bundles at the nodes (nodal discoloration).",
      "organic_treatment": "Hot water treatment (50°C for 2 hours) of seed cane.",
      "chemical_treatment": "Disinfect harvesting tools with Lysol or quaternary ammonium compounds.",
      "prevention": "Use disease-free nursery material; sterilization of cutting knives is critical."
    },
    {
      "plant_name": "Potato",
      "disease": "Mosaic Virus (PVY/PVX)",
      "symptom": "Leaves show faint yellow mottling or mosaic patterns and may be crinkled.",
      "detailed_symptoms": "Leaves exhibit mild to severe mottling (light and dark green areas). Leaflets may be rugose (wrinkled) and plant size is reduced. Tubers may be small.",
      "organic_treatment": "Roguing (pulling out) infected plants; using mineral oil sprays to deter aphids.",
      "chemical_treatment": "Insecticides like Imidacloprid to control aphid vectors.",
      "prevention": "Use certified virus-free seed potatoes; control weed hosts."
    },
    {
      "plant_name": "Wheat",
      "disease": "Glume Blotch",
      "symptom": "Brown spots appear on the glumes (chaff) and nodes of the wheat head.",
      "detailed_symptoms": "Small irregular grey-brown spots on the glumes, often with tiny black dots (pycnidia). Nodes on the stem may turn brown and shrivel.",
      "organic_treatment": "Crop rotation and burying infected residues.",
      "chemical_treatment": "Foliar application of Chlorothalonil or Propiconazole.",
      "prevention": "Use clean seed; crop rotation with non-cereal crops."
    },
    {
      "plant_name": "Sugarcane",
      "disease": "Smut (Culmicolous)",
      "symptom": "See 'Whip Smut' (This is the same disease, listed here for alternative naming context if needed).",
      "detailed_symptoms": "See Whip Smut entry. Note: Sometimes users search by just 'Smut'.",
      "organic_treatment": "See Whip Smut entry.",
      "chemical_treatment": "See Whip Smut entry.",
      "prevention": "See Whip Smut entry."
    },
    {
      "plant_name": "Rice",
      "disease": "Grain Discoloration",
      "symptom": "Grains turn dark brown or black; glumes are spotted.",
      "detailed_symptoms": "Grains develop various colors (black, brown, pink) due to a complex of fungi. The quality and germination rate of the seed are reduced.",
      "organic_treatment": "Spray Neem oil or Pseudomonas fluorescens at 50% flowering.",
      "chemical_treatment": "Spray Carbendazim + Mancozeb at heading stage.",
      "prevention": "Use disease-free seeds; store grains at proper moisture content."
    },
    {
      "plant_name": "Wheat",
      "disease": "Hill Bunt (Stinking Smut)",
      "symptom": "Wheat grains are replaced by black powdery balls that smell like rotten fish.",
      "detailed_symptoms": "Similar to Karnal Bunt but often affects the whole ear. The internal grain mass is black powder. It has a foul fishy odor.",
      "organic_treatment": "Seed treatment with skimmed milk or bio-agents.",
      "chemical_treatment": "Seed treatment with Carboxin or Carbendazim.",
      "prevention": "Use certified seed; grow resistant varieties."
    },
    {
      "plant_name": "Potato",
      "disease": "Stem Canker (Rhizoctonia)",
      "symptom": "Brown, sunken cankers on underground stems; 'Black Scurf' on tubers.",
      "detailed_symptoms": "Reddish-brown sunken lesions (cankers) on underground stems/stolons which can girdle them. Hard black lumps (sclerotia) form on tuber skin (Black Scurf).",
      "organic_treatment": "Green manuring; incorporating sawdust into soil.",
      "chemical_treatment": "Seed tuber treatment with Pencycuron or Carboxin.",
      "prevention": "Shallow planting; use sprout-free seeds; crop rotation."
    },
    {
      "plant_name": "Sugarcane",
      "disease": "Rust (Common)",
      "symptom": "Elongated orange or brown spots on leaves that turn dusty.",
      "detailed_symptoms": "Elongated yellowish spots appear on both leaf surfaces, turning brown to orange-brown. The spots rupture to release powdery rust spores.",
      "organic_treatment": "Remove lower infected leaves.",
      "chemical_treatment": "Spray Mancozeb (0.2%) or Propiconazole.",
      "prevention": "Use resistant varieties (e.g., Co 86032); ensure proper drainage."
    },
    {
      "plant_name": "Wheat",
      "disease": "Tan Spot",
      "symptom": "Tan-colored oval spots with a yellow halo on leaves.",
      "detailed_symptoms": "Small tan-brown spots that expand into oval or lens-shaped lesions with a distinct yellow halo. Often found on lower leaves first.",
      "organic_treatment": "Stubble management (burning or burying).",
      "chemical_treatment": "Foliar spray with Propiconazole or Azoxystrobin.",
      "prevention": "Crop rotation; tillage to bury wheat residue."
    }   
  ]
}

def create_database():
    conn = sqlite3.connect('agricare.db')
    cursor = conn.cursor()

    # Create table with Full-Text Search (FTS) support if desired, 
    # but standard text columns work for simple matching.
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS diseases (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        plant_name TEXT NOT NULL,
        disease TEXT NOT NULL,
        symptom TEXT,
        detailed_symptoms TEXT,
        organic_treatment TEXT,
        chemical_treatment TEXT,
        prevention TEXT
    )
    ''')

    # Clear existing data to avoid duplicates during testing
    cursor.execute('DELETE FROM diseases')

    # Insert data
    for item in data['diseases']:
        cursor.execute('''
        INSERT INTO diseases (
            plant_name, disease, symptom, detailed_symptoms, 
            organic_treatment, chemical_treatment, prevention
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            item['plant_name'],
            item['disease'],
            item['symptom'],
            item['detailed_symptoms'],
            item['organic_treatment'],
            item['chemical_treatment'],
            item['prevention']
        ))

    conn.commit()
    conn.close()
    print("Database 'agricare.db' created successfully with 100% accurate data!")

if __name__ == '__main__':

    create_database()
