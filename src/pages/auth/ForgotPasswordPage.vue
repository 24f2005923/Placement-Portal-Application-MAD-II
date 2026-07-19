<template>
  <div class="portal-card auth-card p-4 p-md-5">
    <span class="badge badge-soft-primary rounded-pill mb-3">Password Recovery</span>
    <h2 class="fw-bold section-heading mb-2">Forgot your password?</h2>
    <p class="text-muted">
      Enter your registered email address and we will show the reset workflow for this demo frontend.
    </p>

    <form class="row g-3" @submit.prevent>
      <div class="col-12">
        <label class="form-label">Email Address</label>
        <input type="email" class="form-control form-control-lg" placeholder="student@college.edu" />
      </div>
      <div class="col-12">
        <router-link to="/auth/reset-password" class="btn btn-primary btn-lg w-100">Continue</router-link>
      </div>
      <div class="col-12 text-center">
        <router-link to="/auth/login" class="text-muted">Back to login</router-link>
      </div>
    </form>
  </div>
</template>
