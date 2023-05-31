
from typing import NamedTuple

#keep an openai json response in the preds variable and can pass it to the autocode funciton directly if you want to test things that happen after openai without sending it to openai again
# pass the preds variable in to the preds_raw_json var in the autocode function to use it
class SampleGPTResponses(NamedTuple):
    sample_gpt_response_list = [
        "[\n  {\n    \"s\": [\"27447\", \"26952\"],\n    \"a\": [\"01402\"],\n    \"i\": [\"M17.11\", \"M19.041\", \"E08.621\", \"I48.91\", \"N18\"],\n    \"m\": [\"RT\"]\n  },\n  {\n    \"s\": [\"27447\", \"26952\"],\n    \"a\": [\"01402\"],\n    \"i\": [\"M17.11\", \"M19.041\", \"E08.621\", \"I48.91\", \"N18.9\"],\n    \"m\": [\"RT\"]\n  }\n]",
        """
            [\n  {\n    \"s\":[\n      \"27447\",\n      \"26910\"\n    ],\n    \"a\":\"01922\",\n    \"i\":[\n      \"M17.11\",\n      \"S69.11XD\"\n    ],\n    \"m\":[\n\n    ],\n    \"c\":0.9\n  },\n  {\n    \"s\":[\n      \"27447\",\n      \"26910\"\n    ],\n    \"a\":\"01922\",\n    \"i\":[\n      \"M17.11\",\n      \"S69.11XD\"\n    ],\n    \"m\":[\n\n    ],\n    \"c\":0.8\n  }\n]
        """,
        '''
            [
            {
            "s": ["27447", "26040", "64447"],
            "a": ["01214", "64447"],
            "i": ["M17.1", "M79.89", "Z79.4"],
            "m": ["RT"]
            },
            {
            "s": ["27447", "26040", "64447"],
            "a": ["01214", "64447"],
            "i": ["M17.1", "M79.89", "Z79.4"],
            "m": ["RT"]
            }
            ]
        ''',
        """[
            {
                "s": "27447",
                "a": "01402",
                "i": [
                "M17.11",
                "L97.422",
                "I48.91",
                "E11.9",
                "N18"
                ],
                "m": [],
                "doc_idx": 0
            },
            {
                "s": "26160",
                "a": "01810",
                "i": [
                "M17.11",
                "L97.422",
                "I48.91",
                "E11.9",
                "N18"
                ],
                "m": [],
                "doc_idx": 0
            },
            {
                "s": "64420",
                "a": "",
                "i": [
                "M79.605",
                "G89.18",
                "M17.11",
                "M16.11"
                ],
                "m": [
                "50",
                "59",
                "LT"
                ],
                "doc_idx": 1
            },
            {
                "s": "64421",
                "a": "",
                "i": [
                "M79.605",
                "G89.18",
                "M17.11",
                "M16.11"
                ],
                "m": [
                "50",
                "59",
                "LT"
                ],
                "doc_idx": 1
            },
            {
                "s": "64447",
                "a": "",
                "i": [
                "M79.605",
                "G89.18",
                "M17.11",
                "M16.11"
                ],
                "m": [
                "50",
                "59",
                "LT"
                ],
                "doc_idx": 1
            },
            {
                "s": "64448",
                "a": "",
                "i": [
                "M79.605",
                "G89.18",
                "M17.11",
                "M16.11"
                ],
                "m": [
                "50",
                "59",
                "LT"
                ],
                "doc_idx": 1
            },
            {
                "s": "64450",
                "a": "",
                "i": [
                "M79.605",
                "G89.18",
                "M17.11",
                "M16.11"
                ],
                "m": [
                "50",
                "59",
                "LT"
                ],
                "doc_idx": 1
            }
        ]
        """
    ]

class SampleDocuments(NamedTuple):
    anesthesia = [
        """Endoscopic Retrograde Cholangiopancreatography Procedure Note
            Procedure: ERCP with biliary sphincterotomy, biliary stent placement, unsuccessful stone removal viaballooncatheter sweeping and lithotripsy. Pre-operative Diagnosis: Retained CBD stone and obstructive jaundice. Post-operative Diagnosis: same, periampullary duodenal diverticulum.
            Indications: Obstructive jaundice with dilated common bile duct and cbd stone removal
            Sedation: GA
            Pre-Procedure Physical:
            The following portions of the patient's history were reviewed and updated as appropriate: . BP (!) 162/99 | Pulse 85 | Temp 99.5 °F (37.5 °C) (Temporal) | Resp 16 | Ht 5' 5" (1.651 m) | Wt 104lb(47.2kg) | LMP (LMP Unknown) | SpO2 95% | BMI 17.31 kg/m² Procedure Details
            Informed consent was obtained for the procedure, including sedation. Risks of pancreatitis, infection, perforation, hemorrhage, adverse drug reaction and aspiration were discussed. The patient wasplacedintheleft lateral decubitus position. Based on the pre-procedure assessment, including reviewof thepatient'smedical history, medications, allergies, and review of systems, she had been deemed to be anappropriatecandidate for conscious sedation; she was therefore sedated with the medications listed below. Thepatientwas monitored continuously with ECG tracing, pulse oximetry, blood pressure monitoring, anddirect
            observations.
            The duodenoscope was inserted into the mouth and advanced to the third portion of the duodenum; findingsand interventions are described below. The patient tolerated the procedure well, and there werenoimmediatecomplications. She was taken to the recovery area in stable condition. An autotome and hydra-guidewire was passed down the scope and CBD was cannulated withminimal
            difficulty. Cholangiogram was performed and findings below. Sphincterectomy was performedwoanycomplication. The autotome was exchanged for the 9-12 mm balloon stone extractor over theguidewireandpassed into the CBD. Multiple 9-12 mm balloon sweeps were performed from the junction betweentheleftandright hepatic ducts. Unsuccessful extraction. No complications noted. Slightly extended the sphincterectomybut still unsuccessful. Changed to a 12-15 mm balloon catheter wo any success. A lithotripsy basket was passed x 2 wo any success in grabbing and crushing the stone. 2 kits used. Findings:
            -diverticulum, located in the second portion of the duodenum, -biliary ductal dilation, with a maximumcommonduct diameter of 12 mm, -filling defect, 10 mm in size, located in the common bile duct. Specimens: None.
            Anesthesia Record
            Operative Note (continued)
            Op Note by Kwadwo Agyei-Gyamfi, MD at 6/2/2020 5:20 PM (continued) Version 1 of 1 Complications: None; patient tolerated the procedure well.
            Disposition: PACU - hemodynamically stable.
            Condition: stable
            Attending Attestation: I performed the procedure.
            Impression: As above.
            Recommendations:
            Monitor LFTs, CBC. IV fluids 125 cc/hr For 12 hrs. Clear liquids today. Lapchole as and whenpatient labsimprove. Outpatient advanced ERCP with be scheduled with Dr. Henderson in 
        """,
        """Procedure: RIGHT TOTAL KNEE ARTHROPLASTY (Right)\n
            Diagnosis: RIGHT KNEE OSTEOARTHRITIS\n
            ANESTHESIA: General, with peripheral nerve block administered by Dr. Michael Daman Smithson, MD.\n
            FINDINGS: Severe degenerative changes of the right knee consistent with osteoarthritis.\n
            PROCEDURE DETAILS: The patient was brought to the operating room and placed supine on the operating table. After successful induction of anesthesia, the right leg was prepped and draped in the usual sterile fashion. 
            A tourniquet was applied to the right upper thigh. A standard midline incision was made over the knee, and arthrotomy was performed.\n\nSevere osteoarthritic changes were noted. The degenerated portions of the knee joint were resected. 
            Measurements were made, and the appropriate sized prosthetic components were selected. The prosthetic knee joint was then placed without complication.\n\nThe wound was thoroughly irrigated, and the joint was checked for appropriate alignment and range of motion. Hemostasis was achieved, and the joint capsule and skin were closed in layers. 
            We also removed the right 4th finger just proximal to the distal interphalangeal joint via a guillatine method due to unhealing chronic wound. 
            The tourniquet was released, and the patient was awakened from anesthesia.
            PMH: atrial fibrillation, diabetes mellitus on insulin, ckd
        """,
        """Patient: Smith, Jimithy X\nDate of Birth: 01/01/55\nDate of Procedure: 08/06/20\nSurgeon: Wamer Commodore Baker, MD\nAnesthesiologist: Michael Daman Smithson, MD\nProcedure: RIGHT TOTAL KNEE ARTHROPLASTY (Right)\n
            Diagnosis: RIGHT KNEE OSTEOARTHRITIS\n
            ANESTHESIA: General, with peripheral nerve block administered by Dr. Michael Daman Smithson, MD. Fentanyl and ropivacaine were administered for pain management.\n
            FINDINGS: Severe degenerative changes of the right knee consistent with osteoarthritis.\n
            PROCEDURE DETAILS: The patient was brought to the operating room and placed supine on the operating table. After successful induction of anesthesia, the right leg was prepped and draped in the usual sterile fashion. 
            A tourniquet was applied to the right upper thigh. A standard midline incision was made over the knee, and arthrotomy was performed.\n\nSevere osteoarthritic changes were noted. The degenerated portions of the knee joint were resected. 
            Measurements were made, and the appropriate sized prosthetic components were selected. The prosthetic knee joint was then placed without complication.\n\nThe wound was thoroughly irrigated, and the joint was checked for appropriate alignment and range of motion. Hemostasis was achieved, and the joint capsule and skin were closed in layers. 
            We also removed the right 4th finger just proximal to the distal interphalangeal joint via a guillatine method due to unhealing chronic wound. 
            The tourniquet was released, and the patient was awakened from anesthesia.
            PMH: atrial fibrillation, diabetes mellitus on insulin, ckd
        """,
        """
            Colonoscopy Procedure Note
            51 year old female outpatient presenting for average risk colon cancer screening
            Procedure: Colonoscopy
            [AA.1] --screening[AA.2]
            Pre-operative Diagnosis: colon cancer screening
            Post-operative Diagnosis:
            [AA.1] normal[AA.2]
            Sedation: per anesthesia
            Pre-Procedure Physical:
            The following portions of the patient's history were reviewed and updated as appropriate: allergies, currentmedications, past family history, past medical history, past social history, past surgical history andproblemlist. BP 147/74 | Pulse 60 | Temp 97 °F (36.1 °C) (Temporal) | Resp 16 | SpO2 96%ASA Class: 2
            Airway: normal, mallampati score: III (soft and hard palate and base of uvula visible)
            Heart: normal S1 and S2
            Lungs: clear
            Abdomen: soft, nontender, normal bowel sounds
            Mental Status: awake and alert; oriented to person, place, and time
            Procedure Details:
            Informed consent was obtained for the procedure, including sedation. Risks of perforation, hemorrhage, adverse drug reaction and aspiration were discussed. The patient was placed in the left lateral decubitusposition. Based on the pre-procedure assessment, including review of the patient's medical history, medications, allergies, and review of systems, she had been deemed to be an appropriate candidateforsedation. The patient was monitored continuously with ECG tracing, pulse oximetry, blood pressuremonitoring,and direct observations. A digital anorectal examination was performed. The
            [AA.1] colonoscope[AA.2] was
            inserted into the rectum and advanced under direct vision to the
            [AA.1] cecum, which was identifiedbytheileocecal valve and appendiceal orifice
            [AA.2]. The quality of the colonic preparation was
            [AA.1] good[AA.2]. Acarefulinspection was made as the colonoscope was withdrawn, findings and interventions are describedbelow. Thepatient tolerated the procedure
            [AA.1] fairly well[AA.2]. Appropriate photodocumentation
            [AA.1] was[AA.2] obtained.Findings: -
            [AA.1] normal colonoscopy
            [AA.2]
            Specimens:[AA.1] n/[AA.2]a
            Estimated blood loss:
            [AA.1] n/a[AA.2]
            Complications:[AA.1] None; patient tolerated the procedure well.
            [AA.2]
            Disposition:[AA.1] PACU - hemodynamically stable.
            [AA.2]
            Condition:[AA.1] stable[AA.2]
            Impression:[AA.1] normal colonoscopy
            [AA.2]
            Recommendations:[AA.1] Colonoscopy in 10 years
            [AA.2]
    """,
    """
        EGD (Esophagogastroduodenoscopy) and Colonoscopy Procedure Note
        Brandy Huginkiss is a 50 y.o. year old female outpatient
        [AA.1] presenting for EGD to evaluate dyspepsia and heartburn (currently untreated - she's reluctant to start PPI) and colonoscopy for colon cancer screening. Sheis chronically constipated - has not taken a laxative regimen other than this morning's bowel prep.
        [AA.2] She resides in Bespoke, SC (near Myrtle Beach).
        [AA.3]
        ############################################################################Procedure: Esophagogastroduodenoscopy
        [AA.1] --diagnostic[AA.3], Colonoscopy[AA.1] --diagnostic[AA.3]
        Pre-operative Diagnosis:
        [AA.1] GERD, dyspepsia, colon cancer screening
        [AA.2]
        Post-operative Diagnosis:
        [AA.1] retained food in the stomach; limited bowel prep, otherwise normal
        [AA.3]
        Sedation: per anesthesia
        Pre-Procedure Physical:
        [AA.1]
        The following portions of the patient's history were reviewed and updated as appropriate: allergies, currentmedications, past family history, past medical history, past social history, past surgical history andproblemlist.[AA.2]
        BP 118/85 | Pulse 75 | Temp 98.1 °F (36.7 °C) (Temporal) | Resp 16 | LMP (LMP Unknown) | SpO297%ASA Class:[AA.1] 2
        [AA.2]
        Airway:[AA.1] normal[AA.2],
        [AA.1]mallampati score: II (hard and soft palate, upper portion of tonsils anduvulavisible)[AA.2]
        Heart:[AA.1] normal S1 and S2
        [AA.2]
        Lungs:[AA.1] clear[AA.2]
        Abdomen:[AA.1] soft, nontender, normal bowel sounds
        [AA.2]
        Mental Status:[AA.1] awake and alert; oriented to person, place, and time
        [AA.2]
        Procedure Details:
        Informed consent was obtained for the procedure, including conscious sedation. Risks of pancreatitis, infection,perforation, hemorrhage, adverse drug reaction and aspiration were discussed. The patient was placedintheleft lateral decubitus position. Based on the pre- procedure assessment, including reviewof thepatient'smedical history, medications, allergies, and review of systems, she had been deemed to be anappropriatecandidate for sedation. She was monitored continuously with ECG tracing, pulse oximetry, bloodpressuremonitoring, and direct observation. The gastroscope was inserted into the mouth and advancedunder directvision to[AA.1] third portion of the duodenum[AA.3]. A careful inspection was made as the gastroscopewaswithdrawn, including a retroflexed view of the proximal stomach; findings and interventions aredescribedbelow. Appropriate photodocumentation
        [AA.1] was[AA.3] obtained. The patient's gurney was repositioned. A lubricated digital anorectal examination was performed. The[AA.1]
        colonoscope[AA.3] was inserted into the rectum and advanced under direct vision
        [AA.1] with difficultyrequiringapplication of abdominal counterpressure
        [AA.3] to the[AA.1] cecum, which was identified by the ileocecal valveand appendiceal orifice
        [AA.3]. The quality of the colonic preparation was
        [AA.1] limited by a large volumeof redsemiliquid[AA.3].
        [AA.1] With water lavage and scope suction, visualization was adequate to rule out large, raisedlesions. Small or flat lesions, however, may have remained obscured.
        [AA.3]
        A careful inspection was made as the colonoscope was withdrawn. The patient tolerated the procedure[AA.1]
        well[AA.3]. Findings and interventions are described below. Appropriate photodocumentation
        [AA.1] was[AA.3]
        obtained.
        Large amount of retained food in the stomach. On initial inspection this appeared to be blood. Withwaterlavage and careful inspection, the red color appears to be from ingested food or dye (not blood). Otherwisenormal.[AA.3]
        Colonoscopy Findings:[AA.1]
        Redundant colon, copious red-tinged semiliquid throughout
        [AA.3]
        Specimens:[AA.1] n/[AA.3]a
        Estimated blood loss:
        [AA.1] none[AA.3]
        Complications:[AA.1] None; patient tolerated the procedure well.
        [AA.3]
        Disposition:[AA.1] PACU - hemodynamically stable.
        [AA.3]
        Condition:[AA.1] stable[AA.3]
        Impression:[AA.1]
        Findings suggestive of generalized intestinal hypomotility
        [AA.3]
        Recommendations: -
        [AA.1] follow up as scheduled. In the meantime, take miralax 1 TBS daily and dulcolax 10-20 mgPOPRNnoBM for 2 consecutive days. Hold PPI at this time.
        [AA.3]
        """,
    ]
    anesthesia_procedure = [
        """Arterial Line:
            Date/Time: 6/2/2020 8:38 AM
            An arterial line was placed using surface landmarks, in the OR for the following indication(s): continuousbloodpressure monitoring. A Catheter size: 18 gauge. (size), Long (16 cm) (length), Arrow (type) catheter was placed, Seldinger
            technique used, into the Left radial artery, secured by tape, Tegaderm 6x8 and suture. Events:
            patient tolerated procedure well with no complications. Additional notes:
            Under GETA
            The supervising anesthesiologist was
            Attending: Monson Shuh, 
        """,
        """Peripheral Block
            Patient location during procedure: pre-op
            Start time: 6/2/2020 7:00 AM
            End time: 6/2/2020 7:07 AM
            Reason for block: at surgeon's request
            Staffing
            Anesthesiologist: Monson Shuh, MD
            Performed: anesthesiologist
            Preanesthetic Checklist
            Completed: patient identified, site marked, pre-op evaluation, timeout performed, IV checked, risksandbenefits discussed, monitors and equipment checked and anesthesia consent given
            Peripheral Block
            Patient position: Semi-sitting. Prep: ChloraPrep
            Patient monitoring: heart rate, blood pressure and continuous pulse ox
            Block type: supraclavicular
            Injection technique: single-shot
            Needle
            Needle type: Stimuplex
            Needle gauge: 20 gauge. Needle length: 4 in
            Needle localization: ultrasound guidance
            Needle insertion depth: 6 cm
            Assessment
            Injection assessment: negative aspiration for heme, no paresthesia on injection, incremental injectionandlocalvisualized surrounding nerve on ultrasound
            Paresthesia pain: none
            Heart rate change: no
            Slow fractionated injection: yes
            Additional Notes
            Risks/benefits/options discussed with patient. Risks of infection, bleeding,seizures, and nerveinjurydiscussedwith patient. Specific risk of lung injury for supraclavicular blocks discussed with patient. Patient acknowledgesunderstanding of risks and wishes to proceed with block. Sedation with Versed 2 mg IV for block. Patientconsciousness and responsiveness maintained throughout block. Aseptic technique with skinprepwithalcohol wipe and chloraprep. Block performed with ultrasound guidance. Block with Ropivacaine0.5%20mLand and Lidocaine 2% 
        """,
        """Preoperative Diagnosis: Pain in the left leg

            Procedure: Adductor canal and popliteal sciatic nerve block using ultrasound guidance

            Anesthesia: Ropivacaine, 20 ml per nerve block location

            Technique: The patient was placed in the supine position and the left leg was prepped and draped in a sterile manner. Using ultrasound guidance, a 22 gauge needle was introduced into the adductor canal and advanced until visualization of the saphenous nerve. Ropivacaine, 20 ml, was then injected around the nerve. An image of the needle in place was captured and stored for review.

            Next, the needle was introduced into the popliteal fossa and advanced until visualization of the sciatic nerve. Ropivacaine, 20 ml, was then injected around the nerve. An image of the needle in place was captured and stored for review.

            The patient tolerated the procedure well and no complications were encountered.

            Post-procedure Diagnosis: Left leg pain, nerve block in place
        """,
        """Preoperative Diagnosis: Pain in the left and right leg

            Procedure: bilateral Adductor canal and popliteal sciatic nerve blocks using ultrasound guidance

            Anesthesia: Ropivacaine, 20 ml per nerve block location

            Technique: The patient was placed in the supine position and the left leg was prepped and draped in a sterile manner. Using ultrasound guidance, a 22 gauge needle was introduced into the adductor canal and advanced until visualization of the saphenous nerve. Ropivacaine, 20 ml, was then injected around the nerve. An image of the needle in place was captured and stored for review.

            Next, the needle was introduced into the popliteal fossa and advanced until visualization of the sciatic nerve. Ropivacaine, 20 ml, was then injected around the nerve. An image of the needle in place was captured and stored for review.

            The patient tolerated the procedure well and no complications were encountered.

            Post-procedure Diagnosis: bilateral leg pain, nerve block in place
        """,
        """Anesthesia Peripheral Block
            Procedure: Adductor canal nerve block
            Block Type: Adductor canal Date/Time: 6/8/2017 3:51 PM
            Patient Location during procedure: Post-op
            Reason for Block: post-op pain management
            Performed by: Anesthesiologist
            Anesthesiologist: COOPER, SUZANE CLAGGETT
            Preanesthetic checklist: patient identified, IV checked, site marked, risks and benefits discussed, surgical consent, monitors and equipment checked, pre-op evaluation and timeout performed. Patient Position: Supine
            Monitoring: Heart rate, cardiac monitor, continuous pulse ox and BP cuff
            Prep: ChloraPrep
            Laterality: Right
            Injection Technique: Single-shot
            Medications: Bupivacaine
            Strength: 0.25% Dose: 30mL
            Procedures: ultrasound guided and image saved to record
            Needle Type: Pajunk
            Needle Gauge: 21 G
            Needle Length: 9 cm
            Needle Localization: Ultrasound guidance and anatomical landmarks
            Last edited 06/08/17 1553 by Suzane Claggett Cooper, MD
            Procedure Notes (continued)
            Injection Assessment: Patient tolerated procedure well and negative aspiration for heme
        """,
        """Anesthesia Peripheral Block
            Block Type: Adductor canal Date/Time: 6/8/2017 3:51 PM
            Patient Location during procedure: Post-op
            Reason for Block: post-op pain management
            Performed by: Anesthesiologist
            Anesthesiologist: COOPER, SUZANE CLAGGETT
            Preanesthetic checklist: patient identified, IV checked, site marked, risks and benefits discussed, surgical consent, monitors and equipment checked, pre-op evaluation and timeout performed. Patient Position: Supine
            Monitoring: Heart rate, cardiac monitor, continuous pulse ox and BP cuff
            Prep: ChloraPrep
            Laterality: Right
            Injection Technique: Single-shot
            Medications: Bupivacaine
            Strength: 0.25% Dose: 30mL
            Procedures: ultrasound guided and image saved to record
            Needle Type: Pajunk
            Needle Gauge: 21 G
            Needle Length: 9 cm
            Needle Localization: Ultrasound guidance and anatomical landmarks
            Last edited 06/08/17 1553 by Suzane Claggett Cooper, MD
            Procedure Notes (continued)
            Injection Assessment: Patient tolerated procedure well and negative aspiration for heme
        """,
        """Anesthesia Peripheral Block
            Block Type: Popliteal Date/Time: 6/8/2017 3:53 PM
            Patient Location during procedure: Post-op
            Performed by: Anesthesiologist
            Anesthesiologist: COOPER, SUZANE CLAGGETT
            Preanesthetic checklist: patient identified, IV checked, site marked, risks and benefits discussed, surgical consent, monitors and equipment checked, pre-op evaluation and timeout performed. Monitoring: Heart rate, cardiac monitor, continuous pulse ox and BP cuff
            Prep: ChloraPrep
            Injection Technique: Single-shot
            Medications: Bupivacaine
            Strength: 0.25% Dose: 30mL
            Procedures: ultrasound guided and image saved to record
            Needle Type: Pajunk
            Needle Gauge: 21 G
            Needle Length: 9 cm
            Needle Localization: Ultrasound guidance and anatomical landmarks
            Injection Assessment: Patient tolerated procedure well, negative asp
        """,
        """Anesthesia Peripheral Block
            Anesthesia Procedure: Ankle nerve block
            Date/Time: 6/12/2017 1:00 PM
            Performed by: COOPER, SUZANE CLAGGETT
            Authorized by: COOPER, SUZANE CLAGGETT
            Block Type: Ankle
            Patient Location: OR
            Ultrasound Guided: No
            Anesthesiologist: COOPER, SUZANE CLAGGETT
            Performed by: Anesthesiologist
            Preanesthetic Checklist: patient identified, pre-op evaluation, risks and benefits discussed, site marked /verified, surgical consent, IV checked, monitors and equipment checked and timeout performedPatient Position: Supine
            Monitoring: Heart rate, cardiac monitor, continuous pulse ox and BP cuffPatient sedatedOxygenation: Face mask
            Prep: ChloraPrep
            Sterile Technique: hand hygiene performed prior to procedure, sterile gloves, gown, cap, mask andsterile tray
            Local Infiltration: Lidocaine
            Strength: 1.5
            Dose: 20
            Laterality: Left
            Injection Technique: Single-shot
            Medications: Lidocaine
            Additives: Lidocaine
            Strength: 1.5
            Dose: 20
            Procedure Technique: not ultrasound guided
            Needle Type: Short-bevel
            Needle Gauge: 25G
            Needle Length: 1 in
            Nerve Localization: Anatomical landmarks
            Catheter Placement: No
            Test Dose: Negative
        """,
        """ ARTERIAL LINE PLACEMENT
            Date/Time: 6/18/2017 11:52 AM
            Performed by: DING, JUAN MORE
            Authorized by: DONG, JUAN DING
            Consent: Verbal consent obtained. Written consent obtained. Risks and benefits: risks, benefits and alternatives were discussed
            Consent given by: patient and spouse
                    Patient understanding: patient states understanding of the procedure being performedPatient consent: the patient's understanding of the procedure matches consent given
            Procedure consent: procedure consent matches procedure scheduled
            Relevant documents: relevant documents present and verified
            Test results: test results available and properly labeled
            Site marked: the operative site was marked
            Imaging studies: imaging studies available
            Required items: required blood products, implants, devices, and special equipment availablePatient identity confirmed: verbally with patient and arm band
            Time out: Immediately prior to procedure a "time out" was called to verify the correct patient,
            procedure, equipment, support staff and site/side marked as required. Preparation: Patient was prepped and draped in the usual sterile fashion. Local anesthesia used: yes
            Anesthesia: local infiltration
            Anesthesia:
            Local anesthesia used: yes
            Anesthesia: local infiltration
            Local Anesthetic: lidocaine 2% without epinephrine
            Anesthetic total: 2 mL
            Sedation:
            Patient sedated: no
            Patient tolerance: Patient tolerated the procedure well with no immediate complications
        """
    ]
    
    surgical = [
        """Patient: Smith, Jimithy X\nDate of Birth: 01/01/55\nDate of Procedure: 08/06/20\nSurgeon: Wamer Commodore Baker, MD\nAnesthesiologist: Michael Daman Smithson, MD\nProcedure: RIGHT TOTAL KNEE ARTHROPLASTY (Right)\n
            Diagnosis: RIGHT KNEE OSTEOARTHRITIS\n\nPREOPERATIVE DIAGNOSIS: Right knee osteoarthritis\nPOSTOPERATIVE DIAGNOSIS: Right knee osteoarthritis\nPROCEDURE PERFORMED: Right total knee arthroplasty\n\n
            ANESTHESIA: General, with peripheral nerve block administered by Dr. Michael Daman Smithson, MD. Fentanyl and ropivacaine were administered for pain management.\n\n
            FINDINGS: Severe degenerative changes of the right knee consistent with osteoarthritis.\n\n
            PROCEDURE DETAILS: The patient was brought to the operating room and placed supine on the operating table. After successful induction of anesthesia, the right leg was prepped and draped in the usual sterile fashion. 
            A tourniquet was applied to the right upper thigh. A standard midline incision was made over the knee, and arthrotomy was performed.\n\nSevere osteoarthritic changes were noted. The degenerated portions of the knee joint were resected. 
            Measurements were made, and the appropriate sized prosthetic components were selected. The prosthetic knee joint was then placed without complication.\n\nThe wound was thoroughly irrigated, and the joint was checked for appropriate alignment and range of motion. Hemostasis was achieved, and the joint capsule and skin were closed in layers. 
            We also removed the right 4th finger just proximal to the distal interphalangeal joint via a guillatine method due to unhealing chronic wound of the distal finger. 
            The tourniquet was released, and the patient was awakened from anesthesia.
            PMH: atrial fibrillation, diabetes mellitus on insulin, ckd
        """
    ]
    radiology = [
        """History: Abdominal aortic aneurysm.
        Technique: Oral contrast was administered orally to the patient. The patient was fully informed of the
        nature and risks of intravenous contrast. Written informed consent was granted. Non-ionic contrast
        was administered intravenously without complication. A helical CT was acquired from the lung bases
        through the symphysis pubis. Maximum intensity pixel images were reconstructed and reviewed as
        well. Images were reviewed in lung windows, bone windows, and abdominal windows. Delayed
        images were also acquired.
        Findings: Abdomen: The lung bases are clear, and the heart is not enlarged. There is no aneurysmal
        dilatation of the aorta despite extensive vascular calcification. Bony structures reflect the patient's
        age and the muscular structures are all intact.
        The liver, spleen, adrenal glands, pancreas, and gallbladder are all morphologically normal with
        normal enhancement. A 3.1 cm exophytic hypodense mass is seen laterally of the left kidney; this
        lesion appears solid and hypervascular, suspicious for renal cell carcinoma. There is no free air, free
        fluid, or inflammatory change. The stomach and visualized portions of the small bowel and large
        bowel are normal. There is no portal, retroperitoneal, or mesenteric adenopathy. There is no omental
        caking.
        Pelvis: The ureters are normal in course and caliber. The bladder has a normal configuration. The
        uterus is unremarkable but neither ovary is visualized.
        Bony muscular and vascular structures reflect the patient's age without aneurysmal dilatation of
        arterial structures. There is no free air, free fluid, or inflammatory change. The visualized portions of
        the small bowel are normal. Diverticulosis is present in the sigmoid colon without radiographic
        evidence for diverticulitis. There is no pelvic or inguinal adenopathy.
        Impression: Abdomen:
        1. 3.1 cm hypodense but solid exophytic lesion of the left kidney suspicious for renal cell carcinoma.
        2. Vascular calcification but no evidence for aneurysmal dilatation of the aorta.
        Pelvis: Diverticulosis without radiographic evidence for diverticulitis
        """
    ]