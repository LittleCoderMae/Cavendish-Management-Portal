<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dynamic Theming Dashboard</title>
    
    <!-- Load Tailwind CSS -->
    <script src="https://cdn.tailwindcss.com"></script>
    
    <!-- Configure Tailwind to map 'primary' colors to CSS variables -->
    <script>
        tailwind.config = {
            theme: {
                extend: {
                    colors: {
                        // This maps 'primary' to the CSS variable --color-primary-600, etc.
                        primary: {
                            500: 'var(--color-primary-500)',
                            600: 'var(--color-primary-600)', // Main use
                            700: 'var(--color-primary-700)',
                            800: 'var(--color-primary-800)',
                        },
                    },
                },
            }
        }
    </script>
    
    <!-- Custom CSS for Theme Variables and Base Style -->
    <style>
        /* Base Font and Background */
        body {
            font-family: 'Inter', ui-sans-serif, system-ui, sans-serif;
            background-color: #f3f4f6;
            min-height: 100vh;
        }

        /* Default Theme: Indigo */
        :root {
            --color-primary-600: #4F46E5; /* indigo-600 */
            --color-primary-500: #6366F1; /* indigo-500 */
            --color-primary-700: #4338CA; /* indigo-700 */
        }

        /* Teal Theme */
        body[data-theme='teal'] {
            --color-primary-600: #0D9488; /* teal-600 */
            --color-primary-500: #14B8A6; /* teal-500 */
            --color-primary-700: #0F766E; /* teal-700 */
        }

        /* Red Theme */
        body[data-theme='red'] {
            --color-primary-600: #DC2626; /* red-600 */
            --color-primary-500: #F87171; /* red-500 */
            --color-primary-700: #B91C1C; /* red-700 */
        }
    </style>
</head>
<body class="pb-10">

    <!-- Theme Panel & Navigation Header -->
    <header class="sticky top-0 bg-white shadow-md z-10 p-4 border-b">
        <div class="container mx-auto flex justify-between items-center">
            <h1 class="text-2xl font-bold text-gray-800">Results Manager</h1>
            
            <div class="flex items-center space-x-4">
                <!-- Navigation Buttons (Simulating Page Links) -->
                <button id="nav-dashboard" class="py-2 px-4 rounded-lg font-medium bg-gray-100 text-gray-700 hover:bg-gray-200 transition">Dashboard</button>
                <button id="nav-student-view" class="py-2 px-4 rounded-lg font-medium bg-gray-100 text-gray-700 hover:bg-gray-200 transition">Student View</button>
                
                <!-- Theme Panel Dropdown -->
                <div id="theme-panel" class="relative">
                    <button id="theme-button" type="button" class="inline-flex justify-center rounded-lg border border-gray-300 shadow-sm px-4 py-2 bg-white text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition duration-150 ease-in-out">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor" style="color: var(--color-primary-600);">
                            <path fill-rule="evenodd" d="M10 2a1 1 0 011 1v1a1 1 0 11-2 0V3a1 1 0 011-1zm4 8a4 4 0 11-8 0 4 4 0 018 0zm-.424 5.924a1 1 0 01-1.414 0l-.707-.707a1 1 0 011.414-1.414l.707.707a1 1 0 010 1.414zM16 10a1 1 0 110 2h-1a1 1 0 110-2h1zM4 10a1 1 0 110 2h-1a1 1 0 110-2h1zm1.707-4.293a1 1 0 010 1.414l-.707.707a1 1 0 01-1.414-1.414l.707-.707a1 1 0 011.414 0zM10 15a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1z" clip-rule="evenodd" />
                        </svg>
                        Theme
                    </button>

                    <div id="theme-menu" class="origin-top-right absolute right-0 mt-2 w-40 rounded-xl shadow-2xl bg-white ring-1 ring-black ring-opacity-5 hidden" role="menu">
                        <div class="py-1" role="none">
                            <button data-theme="default" class="theme-option text-gray-700 block px-4 py-2 text-sm w-full text-left hover:bg-gray-100 flex items-center transition duration-100 rounded-t-xl">
                                <span class="w-4 h-4 rounded-full bg-indigo-600 mr-2 border border-gray-200"></span> Indigo (Default)
                            </button>
                            <button data-theme="teal" class="theme-option text-gray-700 block px-4 py-2 text-sm w-full text-left hover:bg-gray-100 flex items-center transition duration-100">
                                <span class="w-4 h-4 rounded-full bg-teal-600 mr-2 border border-gray-200"></span> Teal
                            </button>
                            <button data-theme="red" class="theme-option text-gray-700 block px-4 py-2 text-sm w-full text-left hover:bg-gray-100 flex items-center transition duration-100 rounded-b-xl">
                                <span class="w-4 h-4 rounded-full bg-red-600 mr-2 border border-gray-200"></span> Red
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </header>

    <main class="container mx-auto p-4 sm:p-6 lg:p-8 pt-8">
        
        <!-- DASHBOARD VIEW (Initially visible) -->
        <div id="dashboard-view">
            <h2 class="text-3xl font-extrabold text-gray-900 mb-8 border-b pb-2">
                System-Wide Results Analysis
            </h2>

            <!-- Key Metrics Cards (Themed Borders) -->
            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 mb-10">
                <div class="bg-white p-6 rounded-xl shadow-md border-b-4 border-primary-500 hover:shadow-lg transition">
                    <p class="text-sm font-medium text-gray-500">Total Enrollment Records</p>
                    <p class="text-3xl font-bold text-gray-900 mt-1" id="metric-enrollments">150</p>
                </div>
                <div class="bg-white p-6 rounded-xl shadow-md border-b-4 border-green-500 hover:shadow-lg transition">
                    <p class="text-sm font-medium text-gray-500">Distinct Students Graded</p>
                    <p class="text-3xl font-bold text-gray-900 mt-1" id="metric-students">50</p>
                </div>
                <div class="bg-white p-6 rounded-xl shadow-md border-b-4 border-yellow-500 hover:shadow-lg transition">
                    <p class="text-sm font-medium text-gray-500">Distinct Courses Managed</p>
                    <p class="text-3xl font-bold text-gray-900 mt-1" id="metric-courses">5</p>
                </div>
            </div>

            <!-- Grade Distribution Chart (Themed Bars) -->
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
                <div class="bg-white p-6 rounded-xl shadow-lg">
                    <h3 class="text-xl font-semibold text-gray-800 mb-4 border-b pb-2">Grade Distribution</h3>
                    <div id="grade-distribution-chart" class="space-y-4">
                        <!-- Chart content generated by JS -->
                    </div>
                </div>

                <!-- Course Enrollment Counts Table -->
                <div class="bg-white p-6 rounded-xl shadow-lg">
                    <h3 class="text-xl font-semibold text-gray-800 mb-4 border-b pb-2">Top Enrollments</h3>
                    <div class="overflow-x-auto max-h-96">
                        <table class="min-w-full divide-y divide-gray-200">
                            <thead class="bg-gray-50 sticky top-0">
                                <tr>
                                    <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Course</th>
                                    <th class="px-4 py-2 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Enrollments</th>
                                </tr>
                            </thead>
                            <tbody id="course-enrollment-body" class="bg-white divide-y divide-gray-200">
                                <!-- Table content generated by JS -->
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>


        <!-- STUDENT VIEW (Initially hidden) -->
        <div id="student-view" class="hidden">
            <div class="flex justify-between items-center mb-6 border-b pb-2">
                <h2 class="text-3xl font-extrabold text-gray-900">
                    Results for John Doe (12345)
                </h2>
                <!-- Link updated to use primary color -->
                <button onclick="switchPage('dashboard')" class="text-primary-600 hover:text-primary-800 flex items-center transition duration-150 ease-in-out">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-1" viewBox="0 0 20 20" fill="currentColor">
                        <path fill-rule="evenodd" d="M9.707 14.707a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 1.414L7.414 9H15a1 1 0 110 2H7.414l2.293 2.293a1 1 0 010 1.414z" clip-rule="evenodd" />
                    </svg>
                    Back to Dashboard
                </button>
            </div>

            <div class="bg-white p-6 rounded-xl shadow-lg mb-8">
                <h3 class="text-xl font-semibold text-gray-800 mb-4">Student Profile</h3>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                    <p><strong>Student ID:</strong> 12345</p>
                    <p><strong>Email:</strong> john.doe@uni.edu</p>
                    <p class="md:col-span-2"><strong>Program:</strong> Computer Science</p>
                </div>
            </div>

            <h3 class="text-2xl font-bold text-gray-900 mb-4">Enrollment History & Grades</h3>
            <div class="overflow-x-auto bg-white rounded-xl shadow-lg">
                <table class="min-w-full divide-y divide-gray-200">
                    <thead class="bg-gray-50">
                        <tr>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Course Code</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Course Title</th>
                            <th class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">Grade</th>
                        </tr>
                    </thead>
                    <tbody id="student-results-body" class="bg-white divide-y divide-gray-200">
                        <!-- Student results generated by JS -->
                    </tbody>
                </table>
            </div>
        </div>

    </main>

    <script>
        // --- MOCK DATA ---
        const MOCK_DATA = {
            gradeDistribution: [
                { grade: 'A', count: 40 },
                { grade: 'B', count: 50 },
                { grade: 'C', count: 30 },
                { grade: 'D', count: 15 },
                { grade: 'F', count: 15 },
            ],
            courseEnrollments: [
                { code: 'CS101', title: 'Intro to Programming', count: 55 },
                { code: 'CS205', title: 'Data Structures', count: 40 },
                { code: 'MA101', title: 'Calculus I', count: 35 },
                { code: 'PH102', title: 'Physics Basics', count: 20 },
            ],
            studentResults: [
                { code: 'CS101', title: 'Intro to Programming', grade: 'A' },
                { code: 'CS205', title: 'Data Structures', grade: 'B' },
                { code: 'MA101', title: 'Calculus I', grade: 'C' },
                { code: 'PH102', title: 'Physics Basics', grade: 'F' },
            ]
        };
        const totalEnrollments = MOCK_DATA.gradeDistribution.reduce((sum, item) => sum + item.count, 0);

        // --- PAGE/VIEW CONTROL ---
        const dashboardView = document.getElementById('dashboard-view');
        const studentView = document.getElementById('student-view');

        window.switchPage = function(pageName) {
            if (pageName === 'dashboard') {
                dashboardView.classList.remove('hidden');
                studentView.classList.add('hidden');
            } else if (pageName === 'student-view') {
                dashboardView.classList.add('hidden');
                studentView.classList.remove('hidden');
            }
        }
        document.getElementById('nav-dashboard').addEventListener('click', () => switchPage('dashboard'));
        document.getElementById('nav-student-view').addEventListener('click', () => switchPage('student-view'));


        // --- THEME SWITCHING LOGIC ---
        
        function applyTheme(theme) {
            const body = document.body;
            const validThemes = ['default', 'teal', 'red'];
            
            // Default to 'default' if theme is invalid or not set
            if (!validThemes.includes(theme)) {
                theme = 'default';
            }
            
            // Set data attribute and save to storage
            body.setAttribute('data-theme', theme);
            localStorage.setItem('selectedTheme', theme);
        }

        function setupThemeListeners() {
            const themeMenu = document.getElementById('theme-menu');
            const themeButton = document.getElementById('theme-button');
            const themePanel = document.getElementById('theme-panel');
            const themeOptions = document.querySelectorAll('.theme-option');

            // Toggle menu visibility
            themeButton.addEventListener('click', (e) => {
                e.stopPropagation(); // Prevent closing immediately
                themeMenu.classList.toggle('hidden');
            });

            // Handle theme selection
            themeOptions.forEach(option => {
                option.addEventListener('click', (e) => {
                    const newTheme = e.currentTarget.getAttribute('data-theme');
                    applyTheme(newTheme);
                    themeMenu.classList.add('hidden'); // Close menu after selection
                });
            });

            // Close the dropdown if the user clicks outside of it
            window.addEventListener('click', (e) => {
                if (!themePanel.contains(e.target) && !themeMenu.classList.contains('hidden')) {
                    themeMenu.classList.add('hidden');
                }
            });
            
            // Load saved theme on initial load
            const savedTheme = localStorage.getItem('selectedTheme') || 'default';
            applyTheme(savedTheme);
        }


        // --- RENDERING MOCK DASHBOARD CONTENT ---

        function renderDashboardContent() {
            // 1. Grade Distribution Chart
            const chart = document.getElementById('grade-distribution-chart');
            const maxCount = MOCK_DATA.gradeDistribution.reduce((max, item) => Math.max(max, item.count), 0);
            
            let chartHTML = '';
            MOCK_DATA.gradeDistribution.forEach(item => {
                const percentageBar = (item.count / maxCount) * 100;
                const percentageTotal = (item.count / totalEnrollments) * 100;

                chartHTML += `
                    <div class="flex items-center space-x-2">
                        <div class="w-12 text-sm font-medium">${item.grade}</div>
                        <div class="flex-grow bg-gray-100 rounded-full h-6">
                            <!-- Themed bar color: bg-primary-600 -->
                            <div class="bg-primary-600 h-6 rounded-full text-xs font-bold text-white flex items-center justify-end px-2 transition-all duration-500"
                                style="width: ${percentageBar.toFixed(2)}%;">
                                ${item.count}
                            </div>
                        </div>
                        <div class="w-12 text-sm text-gray-600 text-right font-medium">${percentageTotal.toFixed(1)}%</div>
                    </div>
                `;
            });
            chart.innerHTML = chartHTML;

            // 2. Course Enrollment Table
            const enrollmentBody = document.getElementById('course-enrollment-body');
            let tableHTML = '';
            MOCK_DATA.courseEnrollments
                .sort((a, b) => b.count - a.count)
                .forEach(course => {
                    tableHTML += `
                        <tr>
                            <td class="px-4 py-3 whitespace-nowrap text-sm font-medium text-gray-900">
                                ${course.title} (${course.code})
                            </td>
                            <td class="px-4 py-3 whitespace-nowrap text-sm text-right">
                                <!-- Themed count color: text-primary-700 -->
                                <span class="font-bold text-primary-700">${course.count}</span>
                            </td>
                        </tr>
                    `;
                });
            enrollmentBody.innerHTML = tableHTML;
        }

        // --- RENDERING MOCK STUDENT CONTENT ---

        function renderStudentContent() {
            const resultsBody = document.getElementById('student-results-body');
            let tableHTML = '';
            MOCK_DATA.studentResults.forEach(result => {
                let gradeClass = 'text-gray-500 italic font-normal';
                if (result.grade === 'A' || result.grade === 'B') {
                    gradeClass = 'text-green-600';
                } else if (result.grade === 'F') {
                    gradeClass = 'text-red-600';
                }
                
                tableHTML += `
                    <tr>
                        <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">${result.code}</td>
                        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600">${result.title}</td>
                        <td class="px-6 py-4 whitespace-nowrap text-lg font-bold text-center">
                            <span class="${gradeClass}">
                                ${result.grade}
                            </span>
                        </td>
                    </tr>
                `;
            });
            resultsBody.innerHTML = tableHTML;
        }


        // --- INITIALIZATION ---
        document.addEventListener('DOMContentLoaded', () => {
            setupThemeListeners();
            renderDashboardContent();
            renderStudentContent();
            // Start on the Dashboard view
            switchPage('dashboard');
        });
    </script>
</body>
</html>