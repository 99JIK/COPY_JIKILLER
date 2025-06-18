# --- Internationalization Data ---

LANGUAGES = {
    "EN": {
        # --- Display Names ---
        "theme_display_names": {"superhero": "Dark", "litera": "Light"},
        "analysis_mode_display_names": {
            "text": "Basic (Text)", 
            "python": "Python (AST)", 
            "c": "C/C++ (AST)", 
            "java": "Java (AST)"
        },
        
        # --- Main UI Text ---
        "theme_label": "Theme:",
        "lang_label": "Language:",
        "folder_title": "📁 Target Folder",
        "select_button": "Select Folder",
        "folder_label": "Please select a folder to start.",
        "folder_prefix": "Selected",
        "analysis_title": "⚙️ Analysis Settings",
        "recursive_check": "Include Subfolders",
        "filter_title": "🔍 Filtering",
        "extensions_menu": "Select Extensions",
        "threshold_prefix_label": "Similarity ≥",
        "scan_button": "✔️ Start Scan",
        "stop_button": "❌ Stop",
        "export_button": "💾 Export Results",
        
        # --- Statusbar Text ---
        "status_ready": "Ready.",
        "status_folder_selected": "Ready to scan. Press the 'Start Scan' button.",
        "status_file_count": "Found {count} files. Ready to scan.",
        "status_error_reading": "Error reading files: {error}",
        "status_scanning": "Progress: {percent:.1f}% ({current}/{total}) | ETA: {eta}",
        "status_scan_done": "Scan complete.",
        "status_scan_cancelled": "Scan cancelled by user.",
        "status_no_files": "No files to compare.",
        
        # --- Dialog & Messagebox Text ---
        "dialog_select_folder": "Select Folder to Scan",
        "dialog_warning_title": "Warning",
        "dialog_info_title": "Info",
        "dialog_error_title": "Error",
        "dialog_success_title": "Success",
        "dialog_ok": "OK",
        "dialog_cancel": "Cancel",
        "dialog_add": "Add",
        "dialog_no_folder": "A target folder must be selected before starting the scan.",
        "dialog_scan_error": "An error occurred during the scan: {error}",
        "dialog_export_success": "Results successfully exported to '{file}'.",
        "dialog_export_error": "An error occurred while exporting: {error}",
        "dialog_add_ext_title": "Add Extension",
        "dialog_add_ext_label": "Enter new extension (e.g., .txt):",
        "dialog_manage_ext_title": "Manage Extensions",
        "dialog_manage_ext_label": "Select custom extensions to delete:",
        "dialog_delete_button": "Delete Selected",
        "dialog_invalid_input_title": "Invalid Input",
        "dialog_invalid_ext_msg": "Invalid format. The extension must start with a dot (e.g., .txt).",
        "dialog_no_custom_ext": "No custom extensions to delete.",
        "all_files": "All Files (*.*)",
        
        # --- Info Window Text ---
        "info_title": "ℹ️ COPY_JIKILLER Info",
        "info_usage_title": "How to Use",
        "info_usage_text": "1.  📁 Select Folder: Choose the folder containing the code files.\n\n2.  ⚙️ Analysis Settings:\n    • Analysis Mode: Select the mode matching the language for best accuracy.\n    • Include Subfolders: Check to scan all subdirectories.\n\n3.  🔍 Filtering:\n    • Extensions: Manage the file types to be included in the scan.\n    • Similarity Threshold: Set the minimum similarity to display.\n\n4.  ✔️ Start Scan: Begin the analysis after setup.\n\n5.  Results: Double-click an item to open the side-by-side comparison.\n\n6.  💾 Export: Save the current results to a CSV file.",
        "info_ast_title": "What is AST Analysis?",
        "info_ast_text": "AST stands for 'Abstract Syntax Tree'. It represents the code's grammatical structure, ignoring superficial differences like variable names, comments, or spacing. This allows COPY_JIKILLER to effectively detect plagiarism even when attempts are made to hide in it.",
        "info_dev_title": "Information",
        "info_dev_text": "Developer: JIK\nAffiliation: M.S. Student at STLAB, Kyungpook National University\n& Member of Altruistic Hive\n\nLicense: MIT License\n\nThis program was developed with the hope of being a small help \nfor coding tests, reducing the workload of professors and TAs, \nand contributing to student education.",
        
        # --- Treeview Headers ---
        "tree_file1": "File 1",
        "tree_file2": "File 2",
        "tree_similarity": "Similarity (%)"
    },
    "KR": {
        # --- 표시 이름 ---
        "theme_display_names": {"superhero": "다크", "litera": "라이트"},
        "analysis_mode_display_names": {"text": "기본 분석 (텍스트)", "python": "Python (AST)", "c": "C/C++ (AST)", "java": "Java (AST)"},
        
        # --- 메인 UI 텍스트 ---
        "theme_label": "테마:",
        "lang_label": "언어:",
        "folder_title": "📁 대상 폴더",
        "select_button": "폴더 선택",
        "folder_label": "검사를 시작할 폴더를 선택해주세요.",
        "folder_prefix": "선택",
        "analysis_title": "⚙️ 분석 설정",
        "recursive_check": "하위 폴더 포함",
        "filter_title": "🔍 필터링",
        "extensions_menu": "확장자 선택",
        "threshold_prefix_label": "유사도 ≥",
        "scan_button": "✔️ 검사 시작",
        "stop_button": "❌ 중단",
        "export_button": "💾 결과 내보내기",
        
        # --- 상태바 텍스트 ---
        "status_ready": "준비되었습니다.",
        "status_folder_selected": "검사 준비 완료. '검사 시작' 버튼을 누르세요.",
        "status_file_count": "총 {count}개의 파일을 찾았습니다. 검사 준비 완료.",
        "status_error_reading": "파일을 읽는 중 오류가 발생했습니다: {error}",
        "status_scanning": "진행률: {percent:.1f}% ({current}/{total}) | 남은 시간: {eta}",
        "status_scan_done": "검사 완료됨.",
        "status_scan_cancelled": "사용자에 의해 중단됨",
        "status_no_files": "비교할 파일 없음.",
        
        # --- 다이얼로그 및 메시지 박스 텍스트 ---
        "dialog_select_folder": "검사할 폴더를 선택하세요",
        "dialog_warning_title": "경고",
        "dialog_info_title": "정보",
        "dialog_error_title": "오류",
        "dialog_success_title": "성공",
        "dialog_ok": "확인",
        "dialog_cancel": "취소",
        "dialog_add": "추가",
        "dialog_no_folder": "먼저 검사할 폴더를 선택해주세요.",
        "dialog_scan_error": "검사 중 오류가 발생했습니다: {error}",
        "dialog_export_success": "결과를 '{file}' 파일로 성공적으로 내보냈습니다.",
        "dialog_export_error": "결과를 내보내는 중 오류가 발생했습니다: {error}",
        "dialog_add_ext_title": "확장자 추가",
        "dialog_add_ext_label": "새 확장자를 입력하세요 (예: .txt):",
        "dialog_manage_ext_title": "확장자 관리",
        "dialog_manage_ext_label": "삭제할 사용자 추가 확장자를 선택하세요:",
        "dialog_delete_button": "선택 항목 삭제",
        "dialog_invalid_input_title": "잘못된 입력",
        "dialog_invalid_ext_msg": "확장자는 점(.)으로 시작해야 합니다 (예: .txt)",
        "dialog_no_custom_ext": "삭제할 사용자 추가 확장자가 없습니다.",
        "all_files": "모든 파일 (*.*)",
        
        # --- 정보 창 텍스트 ---
        "info_title": "ℹ️ COPY_JIKILLER 정보",
        "info_usage_title": "사용법",
        "info_usage_text": "1.  📁 폴더 선택: 검사할 코드 파일들이 담긴 폴더를 선택합니다.\n\n2.  ⚙️ 분석 설정:\n    • 분석 모드: 언어에 맞는 AST 분석 모드를 선택하면 정확도가 크게 향상됩니다.\n    • 하위 폴더 포함: 체크 시 선택한 폴더 내부의 모든 하위 폴더까지 탐색합니다.\n\n3.  🔍 필터링:\n    • 확장자: 검사할 파일의 확장자를 쉼표(,)로 구분하여 입력합니다.\n    • 유사도 임계값: 이 값 이상의 유사도를 가진 결과만 목록에 표시합니다.\n\n4.  ✔️ 검사 시작: 설정을 마친 후 검사를 시작합니다.\n\n5.  결과 확인: 목록의 항목을 더블클릭하면 두 코드를 나란히 비교하는 뷰어가 열립니다.\n\n6.  💾 결과 내보내기: 현재 결과 목록을 CSV 파일로 저장합니다.",
        "info_ast_title": "AST 분석이란?",
        "info_ast_text": "AST는 '추상 구문 트리'의 약자입니다. 코드를 단순히 글자의 나열로 보지 않고, 컴파일러처럼 문법 구조를 파악하여 비교합니다. 이를 통해 변수명 변경, 코드 순서 변경 등에도 정확한 분석이 가능합니다.",
        "info_dev_title": "정보",
        "info_dev_text": "개발자: JIK\n소속: 경북대학교 STLAB 석사과정 & Altruistic Hive\n\n라이선스: MIT License\n\n이 프로그램은 코딩 테스트 및 교수님, \nTA들의 노고와 학생들의 교육에 조금이나마 도움이 \n됐으면 하는 마음에서 개발되었습니다.",
        
        # --- 결과 목록 헤더 ---
        "tree_file1": "파일 1",
        "tree_file2": "파일 2",
        "tree_similarity": "유사도 (%)"
    }
}