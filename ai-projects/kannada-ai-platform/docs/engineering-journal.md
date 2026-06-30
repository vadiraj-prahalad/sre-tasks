## Example: Dr. Rajkumar Knowledge Flow

### User Inputs Tested

| User Input | Internal Normalized Question | Response Source |
|---|---|---|
| `ಡಾ. ರಾಜ್‌ಕುಮಾರ್ ಯಾರು?` | `ಡಾ. ರಾಜ್‌ಕುಮಾರ್ ಯಾರು?` | Trusted JSON |
| `who is dr rajkumar` | `ಡಾ. ರಾಜ್‌ಕುಮಾರ್ ಯಾರು?` | Query Normalizer → Trusted JSON |

### Trusted Answer

ಡಾ. ರಾಜ್‌ಕುಮಾರ್ ಕನ್ನಡ ಚಿತ್ರರಂಗದ ದಿಗ್ಗಜ ನಟ, ಗಾಯಕ ಮತ್ತು ಕರ್ನಾಟಕದ ಸಾಂಸ್ಕೃತಿಕ ಪ್ರತೀಕಗಳಲ್ಲಿ ಒಬ್ಬರು. ಅವರ ಮೂಲ ಹೆಸರು ಸಿಂಗಾನಲ್ಲೂರು ಪುಟ್ಟಸ್ವಾಮಯ್ಯ ಮುತ್ತುರಾಜು. ಅವರು ಸುಮಾರು 200ಕ್ಕೂ ಹೆಚ್ಚು ಕನ್ನಡ ಚಿತ್ರಗಳಲ್ಲಿ ನಟಿಸಿದ್ದಾರೆ ಮತ್ತು ಕನ್ನಡ ಭಾಷೆ ಹಾಗೂ ಸಂಸ್ಕೃತಿಯ ಪ್ರಸಾರಕ್ಕೆ ಮಹತ್ವದ ಕೊಡುಗೆ ನೀಡಿದ್ದಾರೆ. ಅವರಿಗೆ ಭಾರತದ ಅತ್ಯುನ್ನತ ಚಲನಚಿತ್ರ ಗೌರವವಾದ ದಾದಾಸಾಹೇಬ್ ಫಾಲ್ಕೆ ಪ್ರಶಸ್ತಿ ಲಭಿಸಿದೆ.

### Request Flow

```text
User: who is dr rajkumar
 ↓
FastAPI /ask endpoint
 ↓
router.py
 ↓
query_normalizer.py
 ↓
Normalized question: ಡಾ. ರಾಜ್‌ಕುಮಾರ್ ಯಾರು?
 ↓
knowledge_service.py
 ↓
knowledge_repository.py
 ↓
kannada_facts.json
 ↓
Trusted Kannada response
