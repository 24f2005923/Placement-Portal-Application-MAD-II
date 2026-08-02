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
