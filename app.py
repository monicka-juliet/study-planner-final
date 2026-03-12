<script>
const password = document.getElementById("password");
const eye = document.getElementById("toggleEye");
const eyeSlash = document.getElementById("eyeSlash");
const eyeOpen = document.getElementById("eyeOpen");

eye.addEventListener("mouseenter", function() {
    password.type = "text";
    eyeSlash.style.display = "none";
    eyeOpen.style.display = "block";
});

eye.addEventListener("mouseleave", function() {
    password.type = "password";
    eyeSlash.style.display = "block";
    eyeOpen.style.display = "none";
});
</script>
