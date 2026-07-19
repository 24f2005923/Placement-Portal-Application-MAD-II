<template>
  <div class="portal-card auth-card p-4 p-md-5">
    <span class="badge badge-soft-success rounded-pill mb-3">Reset Password</span>
    <h2 class="fw-bold section-heading mb-2">Create a new password</h2>
    <p class="text-muted">
      Use a strong password to secure the placement portal account.
    </p>

    <form class="row g-3" @submit.prevent>
      <div class="col-12">
        <label class="form-label">New Password</label>
        <input type="password" class="form-control form-control-lg" placeholder="New password" />
      </div>
      <div class="col-12">
        <label class="form-label">Confirm Password</label>
        <input type="password" class="form-control form-control-lg" placeholder="Confirm password" />
      </div>
      <div class="col-12">
        <button type="button" class="btn btn-primary btn-lg w-100">Update Password</button>
      </div>
      <div class="col-12 text-center">
        <router-link to="/auth/login" class="text-muted">Return to login</router-link>
      </div>
    </form>
  </div>
</template>
