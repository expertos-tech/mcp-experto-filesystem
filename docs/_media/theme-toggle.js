(function () {
  const STORAGE_KEY = "docs-theme";

  function syncButton(theme) {
    const button = document.getElementById("theme-toggle");

    if (!button) {
      return;
    }

    button.setAttribute(
      "aria-label",
      theme === "dark" ? "Switch to light mode" : "Switch to dark mode"
    );
    button.setAttribute("data-theme-state", theme);
  }

  function applyTheme(theme) {
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem(STORAGE_KEY, theme);
    syncButton(theme);
  }

  function toggleTheme() {
    const currentTheme =
      document.documentElement.getAttribute("data-theme") || "light";
    const nextTheme = currentTheme === "dark" ? "light" : "dark";

    applyTheme(nextTheme);
  }

  function init() {
    const initialTheme =
      document.documentElement.getAttribute("data-theme") || "light";
    const button = document.getElementById("theme-toggle");

    syncButton(initialTheme);

    if (button) {
      button.addEventListener("click", toggleTheme);
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
