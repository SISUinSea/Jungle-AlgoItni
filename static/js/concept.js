document.addEventListener("DOMContentLoaded", () => {
  const slug = window.location.pathname.split("/")[2];
  if (!slug || !window.algoitniProgress) return;
  window.algoitniProgress.setLastAlgorithm(slug);
});
