const APPLICATION_BADGES = {
  selected: 'badge-soft-success',
  shortlisted: 'badge-soft-warning',
  interview: 'badge-soft-info',
  rejected: 'badge-soft-danger',
  applied: 'badge-soft-secondary'
}

const DRIVE_BADGES = {
  open: 'badge-soft-success',
  approved: 'badge-soft-success',
  pending: 'badge-soft-warning',
  closed: 'badge-soft-secondary',
  rejected: 'badge-soft-danger'
}

export function applicationBadge(status) {
  return APPLICATION_BADGES[String(status || '').toLowerCase()] || 'badge-soft-secondary'
}

export function adminApplicationBadge(status) {
  const value = String(status || '').toLowerCase()
  if (value === 'selected') return 'badge-soft-success'
  if (value === 'shortlisted') return 'badge-soft-info'
  if (value === 'interview') return 'badge-soft-warning'
  if (value === 'rejected') return 'badge-soft-danger'
  return 'badge-soft-secondary'
}

export function applicationProgressClass(status) {
  const value = String(status || '').toLowerCase()
  if (value === 'selected') return 'bg-success'
  if (value === 'rejected') return 'bg-danger'
  return 'bg-primary'
}

export function driveBadge(status) {
  return DRIVE_BADGES[String(status || '').toLowerCase()] || 'badge-soft-danger'
}

export function studentPlacementBadge(row) {
  if (row?.status === 'inactive') return 'badge-soft-danger'
  if (row?.placement_status === 'Placed') return 'badge-soft-success'
  if (row?.placement_status === 'Interview') return 'badge-soft-warning'
  return 'badge-soft-primary'
}

export function companyApprovalBadge(company) {
  if (company?.blacklisted) return 'badge-soft-danger'
  return company?.approval_status === 'approved' ? 'badge-soft-success' : 'badge-soft-warning'
}
