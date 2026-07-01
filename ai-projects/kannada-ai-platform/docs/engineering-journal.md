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

```

## 2026-07-01 - Full Stack MVP Milestone

### Completed
- Added SQLite metadata migration
- Added CRUD utilities
- Added search utility
- Added alias resolution
- Added React frontend using Vite
- Connected React frontend to FastAPI backend
- Fixed CORS issue
- Verified UI can ask `madhwa` and receive trusted Kannada answer

### Architecture
Frontend:
React → api.js → FastAPI

Backend:
FastAPI → Router → Alias Resolver → Knowledge Service → Repository → SQLite

Admin:
CLI Tools → Knowledge Admin Service → Repository → SQLite

### Important Learnings
- Swagger is developer API UI
- CORS controls browser-to-backend access
- React uses state to update UI
- Frontend should use services/api.js instead of calling backend directly inside every component

### Next Session
- Refactor frontend into components:
  - Header
  - Home
  - SearchBox
  - AnswerCard
  - Suggestions
  - Footer
- Improve UI identity around Kannada knowledge platform
- Start PWA setup after component structure
