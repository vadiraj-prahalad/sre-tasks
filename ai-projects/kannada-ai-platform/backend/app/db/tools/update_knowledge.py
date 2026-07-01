from app.services.knowledge_admin_service import update_knowledge_answer

def main() -> None:

    canonical_key = "dr_rajkumar"

    updated_answer = (
        "ಡಾ. ರಾಜ್‌ಕುಮಾರ್ (ಸಿಂಗಾನಲ್ಲೂರು ಪುಟ್ಟಸ್ವಾಮಯ್ಯ ಮುತ್ತುರಾಜು) "

        "ಕನ್ನಡ ಚಿತ್ರರಂಗದ ಅತ್ಯಂತ ಗೌರವಾನ್ವಿತ ನಟ, ಗಾಯಕ ಮತ್ತು ಕರ್ನಾಟಕದ "

        "ಸಾಂಸ್ಕೃತಿಕ ಪ್ರತೀಕಗಳಲ್ಲಿ ಒಬ್ಬರು. ಅವರು ಸುಮಾರು 200ಕ್ಕೂ ಹೆಚ್ಚು ಕನ್ನಡ "

        "ಚಿತ್ರಗಳಲ್ಲಿ ನಟಿಸಿದ್ದು, ಕನ್ನಡ ಭಾಷೆ, ಸಂಸ್ಕೃತಿ ಮತ್ತು ಮೌಲ್ಯಗಳನ್ನು "

        "ಜನಮನದಲ್ಲಿ ಬೆಳೆಸುವಲ್ಲಿ ಮಹತ್ವದ ಪಾತ್ರವಹಿಸಿದರು. ಅವರಿಗೆ ದಾದಾಸಾಹೇಬ್ "

        "ಫಾಲ್ಕೆ ಪ್ರಶಸ್ತಿ ಸೇರಿದಂತೆ ಅನೇಕ ಗೌರವಗಳು ಲಭಿಸಿವೆ. ಅಭಿಮಾನಿಗಳು ಅವರನ್ನು "

        "ಪ್ರೀತಿಯಿಂದ ಅಣ್ಣಾವ್ರು ಎಂದು ಕರೆಯುತ್ತಾರೆ."
    )


    update_knowledge_answer(canonical_key, updated_answer)

    print("Knowledge answer updated successfully.")

if __name__ == "__main__":
    main()
