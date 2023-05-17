
from typing import NamedTuple

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
        '''
    ]

class SampleDocuments(NamedTuple):
    anesthesia = [
                """
                Procedure: RIGHT TOTAL KNEE ARTHROPLASTY (Right)\n
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
                """
                Patient: Smith, Jimithy X\nDate of Birth: 01/01/55\nDate of Procedure: 08/06/20\nSurgeon: Wamer Commodore Baker, MD\nAnesthesiologist: Michael Daman Smithson, MD\nProcedure: RIGHT TOTAL KNEE ARTHROPLASTY (Right)\n
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
            ]
    anesthesia_nerveblock = [
                """Preoperative Diagnosis: Pain in the left leg

                    Procedure: Adductor canal and popliteal sciatic nerve block using ultrasound guidance

                    Anesthesia: Ropivacaine, 20 ml per nerve block location

                    Technique: The patient was placed in the supine position and the left leg was prepped and draped in a sterile manner. Using ultrasound guidance, a 22 gauge needle was introduced into the adductor canal and advanced until visualization of the saphenous nerve. Ropivacaine, 20 ml, was then injected around the nerve. An image of the needle in place was captured and stored for review.

                    Next, the needle was introduced into the popliteal fossa and advanced until visualization of the sciatic nerve. Ropivacaine, 20 ml, was then injected around the nerve. An image of the needle in place was captured and stored for review.

                    The patient tolerated the procedure well and no complications were encountered.

                    Post-procedure Diagnosis: Left leg pain, nerve block in place""",
                    """Preoperative Diagnosis: Pain in the left and right leg

                    Procedure: bilateral Adductor canal and popliteal sciatic nerve blocks using ultrasound guidance

                    Anesthesia: Ropivacaine, 20 ml per nerve block location

                    Technique: The patient was placed in the supine position and the left leg was prepped and draped in a sterile manner. Using ultrasound guidance, a 22 gauge needle was introduced into the adductor canal and advanced until visualization of the saphenous nerve. Ropivacaine, 20 ml, was then injected around the nerve. An image of the needle in place was captured and stored for review.

                    Next, the needle was introduced into the popliteal fossa and advanced until visualization of the sciatic nerve. Ropivacaine, 20 ml, was then injected around the nerve. An image of the needle in place was captured and stored for review.

                    The patient tolerated the procedure well and no complications were encountered.

                    Post-procedure Diagnosis: bilateral leg pain, nerve block in place"""
            ]
    
    surgical = [
                """
                Patient: Smith, Jimithy X\nDate of Birth: 01/01/55\nDate of Procedure: 08/06/20\nSurgeon: Wamer Commodore Baker, MD\nAnesthesiologist: Michael Daman Smithson, MD\nProcedure: RIGHT TOTAL KNEE ARTHROPLASTY (Right)\n
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
                """
                    History: Abdominal aortic aneurysm.
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