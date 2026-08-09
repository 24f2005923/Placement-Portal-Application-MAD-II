/**
 * Frontend Validation Helpers
 */

/**
 * Validates whether the given value is a 10-digit numeric phone number.
 * @param {string|number} phone 
 * @returns {boolean}
 */
export function isValidPhone(phone) {
  if (phone === null || phone === undefined) return false
  const cleanPhone = String(phone).trim()
  return /^\d{10}$/.test(cleanPhone)
}

/**
 * Returns a human-readable validation error message for phone numbers, or null if valid.
 * @param {string|number} phone 
 * @returns {string|null}
 */
export function getPhoneValidationError(phone) {
  if (phone === null || phone === undefined || String(phone).trim() === '') {
    return 'Phone number is required.'
  }
  if (!isValidPhone(phone)) {
    return 'Phone number must be exactly 10 digits.'
  }
  return null
}

/**
 * Evaluates password criteria according to security policy:
 * - Minimum 8 characters
 * - At least one uppercase letter (A-Z)
 * - At least one lowercase letter (a-z)
 * - At least one numeric digit (0-9)
 * - At least one special character
 * @param {string} password 
 * @returns {object} criteria breakdown and overall isValid flag
 */
export function getPasswordCriteria(password) {
  const str = String(password || '')
  const minLength = str.length >= 8
  const hasUppercase = /[A-Z]/.test(str)
  const hasLowercase = /[a-z]/.test(str)
  const hasNumber = /[0-9]/.test(str)
  const hasSpecial = /[^a-zA-Z0-9]/.test(str)
  const isValid = minLength && hasUppercase && hasLowercase && hasNumber && hasSpecial

  return {
    minLength,
    hasUppercase,
    hasLowercase,
    hasNumber,
    hasSpecial,
    isValid
  }
}

/**
 * Returns boolean indicating whether password satisfies security policy.
 * @param {string} password 
 * @returns {boolean}
 */
export function isValidPassword(password) {
  return getPasswordCriteria(password).isValid
}

/**
 * Returns human-friendly validation error message for password or null if valid.
 * @param {string} password 
 * @returns {string|null}
 */
export function getPasswordValidationError(password) {
  if (!password || String(password).trim() === '') {
    return 'Password is required.'
  }
  const criteria = getPasswordCriteria(password)
  if (!criteria.minLength) {
    return 'Password must be at least 8 characters long.'
  }
  if (!criteria.hasUppercase) {
    return 'Password must contain at least one uppercase letter (A-Z).'
  }
  if (!criteria.hasLowercase) {
    return 'Password must contain at least one lowercase letter (a-z).'
  }
  if (!criteria.hasNumber) {
    return 'Password must contain at least one number (0-9).'
  }
  if (!criteria.hasSpecial) {
    return 'Password must contain at least one special character (e.g. !@#$%^&*).'
  }
  return null
}

/**
 * Validates department (letters and spaces only, min 2 chars).
 * @param {string} department 
 * @returns {boolean}
 */
export function isValidDepartment(department) {
  if (!department) return false
  const clean = String(department).trim()
  return clean.length >= 2 && /^[a-zA-Z\s]+$/.test(clean)
}

/**
 * Returns human-friendly validation error message for department or null if valid.
 * @param {string} department 
 * @returns {string|null}
 */
export function getDepartmentValidationError(department) {
  if (!department || String(department).trim() === '') {
    return 'Department is required.'
  }
  const clean = String(department).trim()
  if (clean.length < 2) {
    return 'Department must be at least 2 characters.'
  }
  if (!/^[a-zA-Z\s]+$/.test(clean)) {
    return 'Department must contain letters and spaces only.'
  }
  return null
}

/**
 * Validates name (letters and spaces only, min 2 chars).
 * @param {string} name 
 * @returns {boolean}
 */
export function isValidName(name) {
  if (!name) return false
  const clean = String(name).trim()
  return clean.length >= 2 && /^[a-zA-Z\s]+$/.test(clean)
}

/**
 * Returns human-friendly validation error message for name or null if valid.
 * @param {string} name 
 * @returns {string|null}
 */
export function getNameValidationError(name) {
  if (!name || String(name).trim() === '') {
    return 'Full name is required.'
  }
  const clean = String(name).trim()
  if (clean.length < 2) {
    return 'Full name must be at least 2 characters.'
  }
  if (!/^[a-zA-Z\s]+$/.test(clean)) {
    return 'Full name must contain letters and spaces only.'
  }
  return null
}

/**
 * Validates date is not in the past (today or future date).
 * @param {string} dateStr ISO date string (YYYY-MM-DD)
 * @param {string} fieldName
 * @returns {string|null}
 */
export function getDateNotPastValidationError(dateStr, fieldName = 'Date') {
  if (!dateStr || String(dateStr).trim() === '') return null
  const parts = String(dateStr).trim().split('-')
  if (parts.length === 3) {
    const selDate = new Date(parseInt(parts[0], 10), parseInt(parts[1], 10) - 1, parseInt(parts[2], 10))
    const today = new Date()
    today.setHours(0, 0, 0, 0)
    if (selDate < today) {
      return `${fieldName} must be today or a future date.`
    }
  }
  return null
}

/**
 * Returns human-friendly validation error for contact person or null if valid.
 * @param {string} contactPerson
 * @returns {string|null}
 */
export function getContactPersonValidationError(contactPerson) {
  if (!contactPerson || String(contactPerson).trim() === '') return null
  const clean = String(contactPerson).trim()
  if (!/^[a-zA-Z\s]+$/.test(clean)) {
    return 'Contact person must contain letters and spaces only.'
  }
  return null
}

/**
 * Returns human-friendly validation error for website or null if valid.
 * Website must start with 'www.' and end with '.com' or '.in'.
 * @param {string} website
 * @returns {string|null}
 */
export function getWebsiteValidationError(website) {
  if (!website || String(website).trim() === '') return null
  const clean = String(website).trim().toLowerCase()
  if (!clean.startsWith('www.') || (!clean.endsWith('.com') && !clean.endsWith('.in'))) {
    return 'Website must start with www. and end with .com or .in'
  }
  return null
}


