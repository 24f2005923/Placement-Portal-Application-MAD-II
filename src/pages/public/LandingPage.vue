<template>
  <div class="landing-page">
    <!-- Navbar -->
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary sticky-top shadow-sm py-3">
      <div class="container">
        <a class="navbar-brand fw-bold d-flex align-items-center" href="#">
          <i class="bi bi-mortarboard-fill me-2 fs-4"></i>
          Placement Portal
        </a>
        <div class="d-flex ms-auto gap-3">
          <router-link to="/auth/login?role=student" class="btn btn-outline-light px-4 rounded-pill fw-medium">Student</router-link>
          <router-link to="/auth/login?role=company" class="btn btn-light text-primary px-4 rounded-pill fw-medium shadow-sm">Company</router-link>
        </div>
      </div>
    </nav>

    <!-- Hero Section -->
    <section id="home" class="hero-section text-white d-flex align-items-center py-5">
      <div class="container py-5">
        <div class="row align-items-center g-5">
          <div class="col-lg-6">
            <span class="badge bg-white text-primary mb-3 px-3 py-2 rounded-pill fw-bold shadow-sm">Launch Your Career Today</span>
            <h1 class="display-3 fw-bold mb-4 lh-sm">Connecting Top Talent with Global Opportunities</h1>
            <p class="lead mb-5 text-white-50">Our Placement Portal bridges the gap between ambitious students and industry-leading companies. Discover your potential and secure your dream job.</p>
            <div class="d-flex gap-3 flex-wrap">
              <router-link to="/auth/login?role=student" class="btn btn-light text-primary btn-lg px-5 rounded-pill fw-bold shadow-sm hover-lift">Get Started</router-link>
            </div>
          </div>
          <div class="col-lg-6 d-none d-lg-block text-center">
            <div class="hero-image-wrapper p-5 rounded-4 shadow-lg bg-white bg-opacity-10 backdrop-blur d-inline-block">
              <i class="bi bi-briefcase text-white" style="font-size: 10rem; opacity: 0.9;"></i>
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
// Landing page script setup
</script>

<style scoped>
.landing-page {
  font-family: 'Inter', system-ui, -apple-system, sans-serif;
}

.hero-section {
  background: linear-gradient(135deg, var(--portal-blue, #1f5eff) 0%, var(--portal-blue-dark, #12389b) 100%);
  min-height: 100vh;
  position: relative;
  overflow: hidden;
}

.hero-section::before {
  content: '';
  position: absolute;
  top: -10%;
  right: -5%;
  width: 500px;
  height: 500px;
  background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0) 70%);
  border-radius: 50%;
  pointer-events: none;
}

.backdrop-blur {
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.hover-lift {
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.hover-lift:hover {
  transform: translateY(-5px);
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.15) !important;
}

.bg-primary {
  background-color: var(--portal-blue, #1f5eff) !important;
}

.text-primary {
  color: var(--portal-blue, #1f5eff) !important;
}
</style>
