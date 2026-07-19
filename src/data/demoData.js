export const stats = {
  admin: [
    { label: 'Total Students', value: '1,248', icon: 'bi-people', tone: 'primary', delta: '+8.4%' },
    { label: 'Total Companies', value: '86', icon: 'bi-buildings', tone: 'success', delta: '+3.2%' },
    { label: 'Active Drives', value: '14', icon: 'bi-megaphone', tone: 'warning', delta: 'Live now' },
    { label: 'Placed Students', value: '743', icon: 'bi-award', tone: 'danger', delta: '+12.1%' }
  ],
  company: [
    { label: 'Total Drives', value: '6', icon: 'bi-megaphone', tone: 'primary', delta: '2 pending' },
    { label: 'Applications Received', value: '264', icon: 'bi-inbox', tone: 'success', delta: '+18.7%' },
    { label: 'Shortlisted Students', value: '52', icon: 'bi-person-check', tone: 'warning', delta: '+9.5%' },
    { label: 'Selected Students', value: '14', icon: 'bi-trophy', tone: 'danger', delta: '2 joined' }
  ],
  student: [
    { label: 'Available Drives', value: '17', icon: 'bi-briefcase', tone: 'primary', delta: '5 closing soon' },
    { label: 'Applied Drives', value: '08', icon: 'bi-send-check', tone: 'success', delta: '3 awaiting' },
    { label: 'Interview Schedule', value: '04', icon: 'bi-calendar-event', tone: 'warning', delta: 'Next 48 hrs' },
    { label: 'Placement Status', value: 'Placed', icon: 'bi-emoji-smile', tone: 'danger', delta: 'In progress' }
  ]
}

export const recentActivities = [
  { title: 'New drive approved for Infosys', meta: '2 minutes ago', tone: 'success' },
  { title: 'Student profile updated: Priya Sharma', meta: '15 minutes ago', tone: 'primary' },
  { title: 'TCS shortlisted 24 candidates', meta: '32 minutes ago', tone: 'warning' },
  { title: 'Company registration pending review', meta: '1 hour ago', tone: 'danger' }
]

export const students = [
  {
    id: 101,
    name: 'Aarav Mehta',
    rollNo: 'CSE-2025-101',
    department: 'Computer Science',
    cgpa: '8.82',
    skills: ['Vue.js', 'Node.js', 'SQL'],
    status: 'Placed',
    placement: 'Infosys'
  },
  {
    id: 102,
    name: 'Priya Sharma',
    rollNo: 'ECE-2025-044',
    department: 'Electronics',
    cgpa: '8.45',
    skills: ['Python', 'Data Analysis', 'Power BI'],
    status: 'Applied',
    placement: 'Awaiting'
  },
  {
    id: 103,
    name: 'Rahul Singh',
    rollNo: 'IT-2025-077',
    department: 'Information Technology',
    cgpa: '7.96',
    skills: ['React', 'Java', 'Cloud'],
    status: 'Interview',
    placement: 'TCS'
  },
  {
    id: 104,
    name: 'Sneha Patil',
    rollNo: 'ME-2025-018',
    department: 'Mechanical',
    cgpa: '8.12',
    skills: ['AutoCAD', 'Manufacturing', 'MATLAB'],
    status: 'Inactive',
    placement: 'Not Placed'
  }
]

export const companies = [
  {
    id: 501,
    name: 'Infosys',
    sector: 'IT Services',
    status: 'Approved',
    contact: 'hr@infosys.com',
    drives: 3,
    city: 'Bengaluru'
  },
  {
    id: 502,
    name: 'TCS',
    sector: 'Technology',
    status: 'Pending',
    contact: 'campus.talent@tcs.com',
    drives: 2,
    city: 'Mumbai'
  },
  {
    id: 503,
    name: 'Cognizant',
    sector: 'Consulting',
    status: 'Blacklisted',
    contact: 'campus@cognizant.com',
    drives: 1,
    city: 'Chennai'
  }
]

export const drives = [
  {
    id: 701,
    company: 'Infosys',
    role: 'Software Engineer',
    package: '6.5 LPA',
    criteria: 'CGPA >= 7.5, No active backlog',
    deadline: '2026-06-28',
    openings: 60,
    status: 'Open'
  },
  {
    id: 702,
    company: 'TCS',
    role: 'Digital Analyst',
    package: '7.2 LPA',
    criteria: 'CGPA >= 7.0, Aptitude test',
    deadline: '2026-06-24',
    openings: 40,
    status: 'Pending Approval'
  },
  {
    id: 703,
    company: 'Wipro',
    role: 'Associate Consultant',
    package: '5.0 LPA',
    criteria: 'All branches eligible',
    deadline: '2026-07-02',
    openings: 50,
    status: 'Closed'
  }
]

export const applications = [
  { drive: 'Infosys SE', student: 'Aarav Mehta', status: 'Shortlisted', stage: 'HR Round' },
  { drive: 'TCS Analyst', student: 'Priya Sharma', status: 'Applied', stage: 'Screening' },
  { drive: 'Wipro Consultant', student: 'Rahul Singh', status: 'Interview', stage: 'Technical' }
]

export const placementHistory = [
  { company: 'Infosys', role: 'Software Engineer', year: '2026', package: '6.5 LPA' },
  { company: 'TCS', role: 'System Engineer', year: '2025', package: '5.0 LPA' }
]

export const notifications = [
  { title: 'Drive update pending', time: '5m ago' },
  { title: '12 new applications received', time: '18m ago' },
  { title: 'Placement report generated', time: '1h ago' }
]

export const breadcrumbMap = {
  adminDashboard: ['Admin', 'Dashboard'],
  studentList: ['Admin', 'Students'],
  companyList: ['Admin', 'Companies'],
  driveList: ['Admin', 'Placement Drives'],
  reports: ['Admin', 'Reports'],
  companyDashboard: ['Company', 'Dashboard'],
  studentDashboard: ['Student', 'Dashboard']
}
