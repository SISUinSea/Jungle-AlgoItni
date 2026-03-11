document.addEventListener("DOMContentLoaded", () => {
  const slug = window.location.pathname.split("/")[2];
  if (!slug || !window.algoitniProgress) return;
  window.localStorage.setItem(window.algoitniProgress.ALGOITNI_LAST_ALGORITHM_KEY, slug);
});
