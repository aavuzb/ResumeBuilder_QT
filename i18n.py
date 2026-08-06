"""
i18n.py
Translations for the app's own interface — sidebar, buttons, field labels,
hints, dialogs — plus the resume's own section headings (Professional
Summary, Core Competencies, ...), so a resume built while the app is set to
Uzbek or Korean comes out with headings in that language too. This never
translates the user's own typed content (name, summary, bullet points,
etc.) — only the tool's fixed chrome and structural labels.

Usage: call set_language("uz") once (or whenever the user changes it), then
t("key") anywhere to look up the string for whatever language is active.
"""

LANGUAGES = {"en": "English", "uz": "O'zbekcha", "ko": "한국어"}
DEFAULT_LANGUAGE = "en"

_EN = {
    "app.window_title": "Resume Builder",
    "app.brand_title": "Resume Builder",
    "app.brand_tag": "Craft a polished resume",
    "app.footer_note": "PySide6 Edition",
    "app.language": "Language",
    "app.step": "Step",
    "badge.professional_title": "Professional Title",
    "badge.contact_info": "Contact Info",
    "preview.updates_automatically": "Updates automatically as you type",

    "nav.personal": "Personal Info",
    "nav.summary": "Professional Summary",
    "nav.skills": "Core Competencies",
    "nav.experience": "Experience",
    "nav.education": "Education",
    "nav.publications": "Publications & Patents",
    "nav.certificates": "Certificates & Languages",
    "nav.additional": "Additional Info",
    "nav.generate": "Preview & Generate",

    # Resume section headings — rendered in the live preview and the
    # exported .docx/.pdf. Deliberately separate keys from nav.* above even
    # where the English text matches, since some languages phrase a sidebar
    # label and a document heading differently.
    "resume.summary": "Professional Summary",
    "resume.skills": "Core Competencies",
    "resume.experience": "Professional Experience",
    "resume.education": "Education",
    "resume.publications": "Publications & Patents",
    "resume.certificates": "Certificates & Languages",
    "resume.additional": "Additional Information",

    "personal.step_title": "Personal Info",
    "personal.step_hint": "This appears at the top of your resume.",
    "personal.full_name": "Full Name",
    "personal.professional_title": "Professional Title  (e.g. AI / Machine Learning Engineer  •  Software Developer)",
    "personal.contact_details": "Contact Details",
    "personal.contact_hint": (
        "Shown together on one line under your name — drag a row (or use the "
        "arrows) to change the order they appear in."
    ),
    "personal.location": "Location",
    "personal.phone": "Phone",
    "personal.email": "Email",
    "personal.visa": "Visa / Work Status",
    "personal.links_title": "Professional Links",
    "personal.links_hint": "LinkedIn, GitHub, portfolio — shown as clickable links under your contact info.",
    "personal.add_link": "+ Add link",
    "personal.link_label_placeholder": "Label (e.g. GitHub)",

    "summary.step_title": "Professional Summary",
    "summary.step_hint": "A short paragraph introducing your background.",

    "skills.step_title": "Core Competencies",
    "skills.step_hint": "Grouped skill lines, e.g. 'LLM & GenAI: Hugging Face, Ollama...'",
    "skills.add_row": "+ Add skill category",

    "experience.step_title": "Professional Experience",
    "experience.step_hint": "Add each company, then add one card per project/deliverable within it.",
    "experience.add_company": "+ Add company / position",
    "experience.remove_company": "Remove this company",
    "experience.job_title": "Job title",
    "experience.company": "Company",
    "experience.employment_type": "Employment Type",
    "experience.start_date": "Start Date",
    "experience.end_date": "End Date",
    "experience.start_date_placeholder": "e.g. Mar 2025",
    "experience.end_date_placeholder": "e.g. Present",
    "experience.company_link": "Company link (optional — makes the company name clickable)",
    "experience.projects_heading": "Projects at this company",
    "experience.add_project": "+ Add project",
    "experience.remove_project": "Remove project",
    "experience.project_name": "Project / Deliverable",
    "experience.project_link": "Project link (optional — makes the name clickable)",
    "experience.bullets": "Bullet points (one per line)",

    "employment.full_time": "Full-time",
    "employment.part_time": "Part-time",
    "employment.contract": "Contract",
    "employment.freelance": "Freelance",

    "education.step_title": "Education",
    "education.step_hint": "Degrees, most recent first.",
    "education.add": "+ Add education",
    "education.degree": "Degree",
    "education.school": "School / Location",
    "education.school_link": "University link (optional — makes the school name clickable)",
    "education.meta": "Dates  |  GPA  |  Thesis  (shown in italics)",

    "publications.step_title": "Publications & Patents",
    "publications.step_hint": "Add one card per publication or patent — title plus venue, date, or patent number.",
    "publications.add": "+ Add publication or patent",
    "publications.title": "Title",
    "publications.detail": "Detail  (journal / conference, date, patent no.)",

    "certificates.step_title": "Certificates & Languages",
    "certificates.step_hint": "e.g. 'Korean Language: TOPIK Level 4'",
    "certificates.add_row": "+ Add row",

    "additional.step_title": "Additional Information",
    "additional.step_hint": "Nationality, interests, or anything else.",
    "additional.add_row": "+ Add row",

    "generate.step_title": "Preview & Generate",
    "generate.step_hint": (
        "Your live preview updates on the right as you type. Save your progress "
        "or export the final resume below."
    ),
    "generate.live_preview": "Live Preview",
    "generate.preview_hint": "If you've hidden the preview panel, bring it back here.",
    "generate.draft": "Draft",
    "generate.save_draft": "Save Draft (.json)",
    "generate.load_draft": "Load Draft (.json)",
    "generate.export": "Export",
    "generate.generate_docx": "Generate Resume (.docx)",
    "generate.generate_pdf": "Generate Resume (.pdf)",

    "common.label_placeholder": "Label",
    "common.details_placeholder": "Details",
    "common.url_placeholder": "https://...",
    "common.remove": "Remove",
    "common.remove_row": "Remove row",
    "common.add_row": "+ Add row",
    "common.drag_reorder": "Drag to reorder",
    "common.drag_reorder_section": "Drag to reorder this section",
    "common.move_section_up": "Move this section up",
    "common.move_section_down": "Move this section down",
    "common.move_up": "Move up",
    "common.move_down": "Move down",
    "common.reset_order": "↺  Reset order",
    "common.hide_preview": "Hide preview  »",
    "common.show_preview": "Show preview  «",
    "common.style_settings": "🎨 Style Settings",

    "style.title": "Resume Style",
    "style.hint": "Changes apply instantly — to the live preview and to what you export.",
    "style.presets": "Quick presets",
    "style.choose_preset": "Choose a preset…",
    "style.font": "Font",
    "style.font_sizes": "Font sizes (pt)",
    "style.size_name": "Name",
    "style.size_title": "Professional title",
    "style.size_heading": "Section headings",
    "style.size_body": "Body text",
    "style.size_meta": "Dates / meta text",
    "style.colors": "Colors",
    "style.color_accent": "Headings && name",
    "style.color_accent_soft": "Company / school names",
    "style.color_highlight": "Section rule accent",
    "style.color_text": "Body text",
    "style.color_muted": "Dates && meta text",
    "style.color_background": "Page background",
    "style.bg_note": (
        "Page background shows in the live preview and in Word — PDF export via "
        "the LibreOffice fallback may render it as white. Generate the .docx to be sure."
    ),
    "style.reset_default": "Reset to Default",
    "style.close": "Close",
    "style.choose_color": "Choose color",

    "status.ready": "Ready.",
    "status.section_order_updated": "Section order updated.",
    "status.section_order_reset": "Section order reset to default.",
    "status.contact_order_updated": "Contact field order updated.",
    "status.resume_style_updated": "Resume style updated.",
    "status.draft_saved": "Draft saved to {path}",
    "status.draft_loaded": "Draft loaded from {path}",
    "status.resume_generated": "Resume generated: {path}",
    "status.generating_pdf": "Generating PDF…",
    "status.pdf_failed": "PDF generation failed.",

    "dialog.save_draft_title": "Save Draft",
    "dialog.load_draft_title": "Load Draft",
    "dialog.error_loading_draft": "Error loading draft",
    "dialog.missing_name_title": "Missing name",
    "dialog.missing_name_msg": "Please enter your name in Personal Info first.",
    "dialog.generate_resume_title": "Generate Resume",
    "dialog.error_generating_resume": "Error generating resume",
    "dialog.error_generating_pdf": "Error generating PDF",
    "dialog.success_title": "Success",
    "dialog.success_msg": "Your resume was generated:\n{path}",

    "filter.json_files": "JSON files (*.json)",
    "filter.word_document": "Word Document (*.docx)",
    "filter.pdf_document": "PDF Document (*.pdf)",
}

_UZ = {
    "app.window_title": "Rezyume Tuzuvchi",
    "app.brand_title": "Rezyume Tuzuvchi",
    "app.brand_tag": "Sayqallangan rezyume yarating",
    "app.footer_note": "PySide6 nashri",
    "app.language": "Til",
    "app.step": "Qadam",
    "badge.professional_title": "Kasbiy Lavozim",
    "badge.contact_info": "Aloqa Ma'lumotlari",
    "preview.updates_automatically": "Yozayotganingizda avtomatik yangilanadi",

    "nav.personal": "Shaxsiy Ma'lumotlar",
    "nav.summary": "Kasbiy Xulosa",
    "nav.skills": "Asosiy Ko'nikmalar",
    "nav.experience": "Tajriba",
    "nav.education": "Ta'lim",
    "nav.publications": "Nashrlar va Patentlar",
    "nav.certificates": "Sertifikatlar va Tillar",
    "nav.additional": "Qo'shimcha Ma'lumot",
    "nav.generate": "Ko'rish va Yaratish",

    "resume.summary": "Kasbiy Xulosa",
    "resume.skills": "Asosiy Ko'nikmalar",
    "resume.experience": "Kasbiy Tajriba",
    "resume.education": "Ta'lim",
    "resume.publications": "Nashrlar va Patentlar",
    "resume.certificates": "Sertifikatlar va Tillar",
    "resume.additional": "Qo'shimcha Ma'lumotlar",

    "personal.step_title": "Shaxsiy Ma'lumotlar",
    "personal.step_hint": "Bu rezyumeningiz yuqorisida ko'rinadi.",
    "personal.full_name": "To'liq Ism",
    "personal.professional_title": "Kasbiy Lavozim  (masalan, AI / Mashinali O'rganish Muhandisi  •  Dasturchi)",
    "personal.contact_details": "Aloqa Ma'lumotlari",
    "personal.contact_hint": (
        "Ismingiz ostida bitta qatorda ko'rsatiladi — tartibini o'zgartirish uchun "
        "qatorni suring (yoki strelkalardan foydalaning)."
    ),
    "personal.location": "Manzil",
    "personal.phone": "Telefon",
    "personal.email": "Elektron pochta",
    "personal.visa": "Viza / Ish maqomi",
    "personal.links_title": "Kasbiy Havolalar",
    "personal.links_hint": "LinkedIn, GitHub, portfolio — aloqa ma'lumotlari ostida bosiladigan havola sifatida ko'rsatiladi.",
    "personal.add_link": "+ Havola qo'shish",
    "personal.link_label_placeholder": "Nom (masalan, GitHub)",

    "summary.step_title": "Kasbiy Xulosa",
    "summary.step_hint": "O'zingiz haqingizda qisqacha paragraf.",

    "skills.step_title": "Asosiy Ko'nikmalar",
    "skills.step_hint": "Guruhlangan ko'nikma qatorlari, masalan: 'LLM & GenAI: Hugging Face, Ollama...'",
    "skills.add_row": "+ Ko'nikma toifasini qo'shish",

    "experience.step_title": "Kasbiy Tajriba",
    "experience.step_hint": "Har bir kompaniyani qo'shing, so'ng ichiga loyiha/natija bo'yicha kartochka qo'shing.",
    "experience.add_company": "+ Kompaniya / lavozim qo'shish",
    "experience.remove_company": "Bu kompaniyani o'chirish",
    "experience.job_title": "Lavozim",
    "experience.company": "Kompaniya",
    "experience.employment_type": "Bandlik turi",
    "experience.start_date": "Boshlanish sanasi",
    "experience.end_date": "Tugash sanasi",
    "experience.start_date_placeholder": "masalan, 2025-mart",
    "experience.end_date_placeholder": "masalan, Hozirgacha",
    "experience.company_link": "Kompaniya havolasi (ixtiyoriy — kompaniya nomini bosiladigan qiladi)",
    "experience.projects_heading": "Ushbu kompaniyadagi loyihalar",
    "experience.add_project": "+ Loyiha qo'shish",
    "experience.remove_project": "Loyihani o'chirish",
    "experience.project_name": "Loyiha / Natija",
    "experience.project_link": "Loyiha havolasi (ixtiyoriy — nomini bosiladigan qiladi)",
    "experience.bullets": "Vazifalar ro'yxati (har birini alohida qatorda yozing)",

    "employment.full_time": "To'liq stavka",
    "employment.part_time": "Yarim stavka",
    "employment.contract": "Shartnoma",
    "employment.freelance": "Frilanser",

    "education.step_title": "Ta'lim",
    "education.step_hint": "Darajalar, so'nggisidan boshlab.",
    "education.add": "+ Ta'lim qo'shish",
    "education.degree": "Daraja",
    "education.school": "Maktab / Manzil",
    "education.school_link": "Universitet havolasi (ixtiyoriy — maktab nomini bosiladigan qiladi)",
    "education.meta": "Sanalar  |  GPA  |  Dissertatsiya  (qiya shriftda ko'rsatiladi)",

    "publications.step_title": "Nashrlar va Patentlar",
    "publications.step_hint": "Har bir nashr yoki patent uchun kartochka qo'shing — sarlavha, manba, sana yoki patent raqami.",
    "publications.add": "+ Nashr yoki patent qo'shish",
    "publications.title": "Sarlavha",
    "publications.detail": "Tafsilot  (jurnal / konferensiya, sana, patent raqami)",

    "certificates.step_title": "Sertifikatlar va Tillar",
    "certificates.step_hint": "masalan, 'Koreys tili: TOPIK 4-daraja'",
    "certificates.add_row": "+ Qator qo'shish",

    "additional.step_title": "Qo'shimcha Ma'lumotlar",
    "additional.step_hint": "Millat, qiziqishlar yoki boshqa har qanday narsa.",
    "additional.add_row": "+ Qator qo'shish",

    "generate.step_title": "Ko'rish va Yaratish",
    "generate.step_hint": (
        "Jonli ko'rinish yozayotganingizda o'ng tomonda yangilanadi. Jarayoningizni saqlang "
        "yoki yakuniy rezyumeni quyida eksport qiling."
    ),
    "generate.live_preview": "Jonli Ko'rinish",
    "generate.preview_hint": "Agar ko'rinish panelini yashirgan bo'lsangiz, uni shu yerdan qayta oching.",
    "generate.draft": "Qoralama",
    "generate.save_draft": "Qoralamani saqlash (.json)",
    "generate.load_draft": "Qoralamani yuklash (.json)",
    "generate.export": "Eksport qilish",
    "generate.generate_docx": "Rezyume yaratish (.docx)",
    "generate.generate_pdf": "Rezyume yaratish (.pdf)",

    "common.label_placeholder": "Nom",
    "common.details_placeholder": "Tafsilotlar",
    "common.url_placeholder": "https://...",
    "common.remove": "O'chirish",
    "common.remove_row": "Qatorni o'chirish",
    "common.add_row": "+ Qator qo'shish",
    "common.drag_reorder": "Tartibini o'zgartirish uchun suring",
    "common.drag_reorder_section": "Bu bo'limni suring",
    "common.move_section_up": "Bu bo'limni yuqoriga siljitish",
    "common.move_section_down": "Bu bo'limni pastga siljitish",
    "common.move_up": "Yuqoriga siljitish",
    "common.move_down": "Pastga siljitish",
    "common.reset_order": "↺  Tartibni tiklash",
    "common.hide_preview": "Ko'rinishni yashirish  »",
    "common.show_preview": "Ko'rinishni ko'rsatish  «",
    "common.style_settings": "🎨 Uslub Sozlamalari",

    "style.title": "Rezyume Uslubi",
    "style.hint": "O'zgarishlar darhol qo'llaniladi — jonli ko'rinishga va eksport qilinadigan faylga ham.",
    "style.presets": "Tayyor uslublar",
    "style.choose_preset": "Uslubni tanlang…",
    "style.font": "Shrift",
    "style.font_sizes": "Shrift o'lchamlari (pt)",
    "style.size_name": "Ism",
    "style.size_title": "Kasbiy lavozim",
    "style.size_heading": "Bo'lim sarlavhalari",
    "style.size_body": "Asosiy matn",
    "style.size_meta": "Sanalar / qo'shimcha matn",
    "style.colors": "Ranglar",
    "style.color_accent": "Sarlavhalar va ism",
    "style.color_accent_soft": "Kompaniya / maktab nomlari",
    "style.color_highlight": "Bo'lim chizig'i rangi",
    "style.color_text": "Asosiy matn",
    "style.color_muted": "Sanalar va qo'shimcha matn",
    "style.color_background": "Sahifa foni",
    "style.bg_note": (
        "Sahifa foni jonli ko'rinishda va Word'da ko'rinadi — LibreOffice orqali PDF eksport "
        "qilinganda oq bo'lib chiqishi mumkin. Ishonch hosil qilish uchun .docx yarating."
    ),
    "style.reset_default": "Standartga qaytarish",
    "style.close": "Yopish",
    "style.choose_color": "Rangni tanlang",

    "status.ready": "Tayyor.",
    "status.section_order_updated": "Bo'limlar tartibi yangilandi.",
    "status.section_order_reset": "Bo'limlar tartibi standartga qaytarildi.",
    "status.contact_order_updated": "Aloqa maydonlari tartibi yangilandi.",
    "status.resume_style_updated": "Rezyume uslubi yangilandi.",
    "status.draft_saved": "Qoralama saqlandi: {path}",
    "status.draft_loaded": "Qoralama yuklandi: {path}",
    "status.resume_generated": "Rezyume yaratildi: {path}",
    "status.generating_pdf": "PDF yaratilmoqda…",
    "status.pdf_failed": "PDF yaratib bo'lmadi.",

    "dialog.save_draft_title": "Qoralamani saqlash",
    "dialog.load_draft_title": "Qoralamani yuklash",
    "dialog.error_loading_draft": "Qoralamani yuklashda xatolik",
    "dialog.missing_name_title": "Ism kiritilmagan",
    "dialog.missing_name_msg": "Iltimos, avval Shaxsiy Ma'lumotlar bo'limida ismingizni kiriting.",
    "dialog.generate_resume_title": "Rezyume yaratish",
    "dialog.error_generating_resume": "Rezyume yaratishda xatolik",
    "dialog.error_generating_pdf": "PDF yaratishda xatolik",
    "dialog.success_title": "Muvaffaqiyatli",
    "dialog.success_msg": "Rezyumeingiz yaratildi:\n{path}",

    "filter.json_files": "JSON fayllari (*.json)",
    "filter.word_document": "Word hujjati (*.docx)",
    "filter.pdf_document": "PDF hujjati (*.pdf)",
}

_KO = {
    "app.window_title": "이력서 작성기",
    "app.brand_title": "이력서 작성기",
    "app.brand_tag": "세련된 이력서를 작성하세요",
    "app.footer_note": "PySide6 버전",
    "app.language": "언어",
    "app.step": "단계",
    "badge.professional_title": "직함",
    "badge.contact_info": "연락처 정보",
    "preview.updates_automatically": "입력하는 동안 자동으로 업데이트됩니다",

    "nav.personal": "개인 정보",
    "nav.summary": "전문 요약",
    "nav.skills": "핵심 역량",
    "nav.experience": "경력",
    "nav.education": "학력",
    "nav.publications": "논문 및 특허",
    "nav.certificates": "자격증 및 언어",
    "nav.additional": "추가 정보",
    "nav.generate": "미리보기 및 생성",

    "resume.summary": "전문 요약",
    "resume.skills": "핵심 역량",
    "resume.experience": "경력 사항",
    "resume.education": "학력",
    "resume.publications": "논문 및 특허",
    "resume.certificates": "자격증 및 언어",
    "resume.additional": "추가 정보",

    "personal.step_title": "개인 정보",
    "personal.step_hint": "이력서 상단에 표시됩니다.",
    "personal.full_name": "이름",
    "personal.professional_title": "직함  (예: AI / 머신러닝 엔지니어  •  소프트웨어 개발자)",
    "personal.contact_details": "연락처 정보",
    "personal.contact_hint": "이름 아래 한 줄로 표시됩니다 — 순서를 바꾸려면 항목을 드래그하거나 화살표를 사용하세요.",
    "personal.location": "위치",
    "personal.phone": "전화번호",
    "personal.email": "이메일",
    "personal.visa": "비자 / 취업 상태",
    "personal.links_title": "전문 링크",
    "personal.links_hint": "LinkedIn, GitHub, 포트폴리오 — 연락처 정보 아래 클릭 가능한 링크로 표시됩니다.",
    "personal.add_link": "+ 링크 추가",
    "personal.link_label_placeholder": "이름 (예: GitHub)",

    "summary.step_title": "전문 요약",
    "summary.step_hint": "자신의 배경을 소개하는 짧은 문단.",

    "skills.step_title": "핵심 역량",
    "skills.step_hint": "그룹화된 역량 항목, 예: 'LLM & GenAI: Hugging Face, Ollama...'",
    "skills.add_row": "+ 역량 카테고리 추가",

    "experience.step_title": "경력 사항",
    "experience.step_hint": "각 회사를 추가한 다음, 그 안에 프로젝트/결과물별 카드를 추가하세요.",
    "experience.add_company": "+ 회사 / 직책 추가",
    "experience.remove_company": "이 회사 삭제",
    "experience.job_title": "직책",
    "experience.company": "회사",
    "experience.employment_type": "고용 형태",
    "experience.start_date": "시작일",
    "experience.end_date": "종료일",
    "experience.start_date_placeholder": "예: 2025년 3월",
    "experience.end_date_placeholder": "예: 재직 중",
    "experience.company_link": "회사 링크 (선택 사항 — 회사명을 클릭 가능하게 만듭니다)",
    "experience.projects_heading": "이 회사에서의 프로젝트",
    "experience.add_project": "+ 프로젝트 추가",
    "experience.remove_project": "프로젝트 삭제",
    "experience.project_name": "프로젝트 / 결과물",
    "experience.project_link": "프로젝트 링크 (선택 사항 — 이름을 클릭 가능하게 만듭니다)",
    "experience.bullets": "주요 업무 (한 줄에 하나씩)",

    "employment.full_time": "정규직",
    "employment.part_time": "시간제",
    "employment.contract": "계약직",
    "employment.freelance": "프리랜서",

    "education.step_title": "학력",
    "education.step_hint": "학위, 최신순으로.",
    "education.add": "+ 학력 추가",
    "education.degree": "학위",
    "education.school": "학교 / 위치",
    "education.school_link": "대학교 링크 (선택 사항 — 학교명을 클릭 가능하게 만듭니다)",
    "education.meta": "기간  |  학점  |  논문  (이탤릭체로 표시됨)",

    "publications.step_title": "논문 및 특허",
    "publications.step_hint": "논문 또는 특허마다 카드를 추가하세요 — 제목, 게재지, 날짜 또는 특허 번호.",
    "publications.add": "+ 논문 또는 특허 추가",
    "publications.title": "제목",
    "publications.detail": "세부 사항  (학술지 / 학회, 날짜, 특허 번호)",

    "certificates.step_title": "자격증 및 언어",
    "certificates.step_hint": "예: '한국어: TOPIK 4급'",
    "certificates.add_row": "+ 항목 추가",

    "additional.step_title": "추가 정보",
    "additional.step_hint": "국적, 관심사, 또는 기타 사항.",
    "additional.add_row": "+ 항목 추가",

    "generate.step_title": "미리보기 및 생성",
    "generate.step_hint": "입력하는 동안 오른쪽에 실시간으로 미리보기가 업데이트됩니다. 진행 상황을 저장하거나 아래에서 최종 이력서를 내보내세요.",
    "generate.live_preview": "실시간 미리보기",
    "generate.preview_hint": "미리보기 패널을 숨겼다면 여기서 다시 표시할 수 있습니다.",
    "generate.draft": "임시 저장",
    "generate.save_draft": "임시 저장 (.json)",
    "generate.load_draft": "임시 저장 불러오기 (.json)",
    "generate.export": "내보내기",
    "generate.generate_docx": "이력서 생성 (.docx)",
    "generate.generate_pdf": "이력서 생성 (.pdf)",

    "common.label_placeholder": "이름",
    "common.details_placeholder": "세부 정보",
    "common.url_placeholder": "https://...",
    "common.remove": "삭제",
    "common.remove_row": "항목 삭제",
    "common.add_row": "+ 항목 추가",
    "common.drag_reorder": "드래그하여 순서 변경",
    "common.drag_reorder_section": "이 섹션을 드래그하여 순서 변경",
    "common.move_section_up": "이 섹션을 위로 이동",
    "common.move_section_down": "이 섹션을 아래로 이동",
    "common.move_up": "위로 이동",
    "common.move_down": "아래로 이동",
    "common.reset_order": "↺  순서 초기화",
    "common.hide_preview": "미리보기 숨기기  »",
    "common.show_preview": "미리보기 표시  «",
    "common.style_settings": "🎨 스타일 설정",

    "style.title": "이력서 스타일",
    "style.hint": "변경 사항은 즉시 적용됩니다 — 실시간 미리보기와 내보내기 결과 모두에요.",
    "style.presets": "빠른 프리셋",
    "style.choose_preset": "프리셋 선택…",
    "style.font": "글꼴",
    "style.font_sizes": "글꼴 크기 (pt)",
    "style.size_name": "이름",
    "style.size_title": "직함",
    "style.size_heading": "섹션 제목",
    "style.size_body": "본문",
    "style.size_meta": "날짜 / 부가 텍스트",
    "style.colors": "색상",
    "style.color_accent": "제목 및 이름",
    "style.color_accent_soft": "회사 / 학교 이름",
    "style.color_highlight": "섹션 구분선 강조색",
    "style.color_text": "본문",
    "style.color_muted": "날짜 및 부가 텍스트",
    "style.color_background": "페이지 배경",
    "style.bg_note": (
        "페이지 배경은 실시간 미리보기와 Word에서 표시됩니다 — LibreOffice를 통한 PDF 내보내기에서는 "
        "흰색으로 표시될 수 있습니다. 확실히 하려면 .docx로 생성하세요."
    ),
    "style.reset_default": "기본값으로 재설정",
    "style.close": "닫기",
    "style.choose_color": "색상 선택",

    "status.ready": "준비 완료.",
    "status.section_order_updated": "섹션 순서가 업데이트되었습니다.",
    "status.section_order_reset": "섹션 순서가 기본값으로 재설정되었습니다.",
    "status.contact_order_updated": "연락처 필드 순서가 업데이트되었습니다.",
    "status.resume_style_updated": "이력서 스타일이 업데이트되었습니다.",
    "status.draft_saved": "임시 저장됨: {path}",
    "status.draft_loaded": "임시 저장 파일을 불러왔습니다: {path}",
    "status.resume_generated": "이력서가 생성되었습니다: {path}",
    "status.generating_pdf": "PDF 생성 중…",
    "status.pdf_failed": "PDF 생성에 실패했습니다.",

    "dialog.save_draft_title": "임시 저장",
    "dialog.load_draft_title": "임시 저장 불러오기",
    "dialog.error_loading_draft": "임시 저장 불러오기 오류",
    "dialog.missing_name_title": "이름 누락",
    "dialog.missing_name_msg": "먼저 개인 정보에 이름을 입력해 주세요.",
    "dialog.generate_resume_title": "이력서 생성",
    "dialog.error_generating_resume": "이력서 생성 오류",
    "dialog.error_generating_pdf": "PDF 생성 오류",
    "dialog.success_title": "성공",
    "dialog.success_msg": "이력서가 생성되었습니다:\n{path}",

    "filter.json_files": "JSON 파일 (*.json)",
    "filter.word_document": "Word 문서 (*.docx)",
    "filter.pdf_document": "PDF 문서 (*.pdf)",
}

_ALL = {"en": _EN, "uz": _UZ, "ko": _KO}

_current_lang = DEFAULT_LANGUAGE


def set_language(lang: str):
    global _current_lang
    _current_lang = lang if lang in _ALL else DEFAULT_LANGUAGE


def get_language() -> str:
    return _current_lang


def t(key: str, lang: str = None, **kwargs) -> str:
    """Look up `key` in `lang` (defaults to the currently active language),
    falling back to English and then to the raw key itself so a missing
    translation degrades to something visible rather than crashing."""
    table = _ALL.get(lang or _current_lang, _EN)
    s = table.get(key, _EN.get(key, key))
    return s.format(**kwargs) if kwargs else s
