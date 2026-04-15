const projectTypeButtons = document.querySelectorAll("[data-type]");
const moduleCheckboxes = document.querySelectorAll(".modules input[type=checkbox]");
const complexityInput = document.querySelector("#complexity");
const complexityValue = document.querySelector("#complexity-value");
const quoteSummary = document.querySelector("#quote-summary");

const state = {
  projectType: "cabinet",
  modules: [],
  complexity: 2,
};

const basePrices = {
  cabinet: 140000,
  integration: 110000,
  ecommerce: 160000,
};

const modulePrices = {
  auth: 30000,
  crm: 45000,
  telegram: 25000,
  analytics: 20000,
  payments: 50000,
};

function estimate(state) {
  const base = basePrices[state.projectType];
  const modulesTotal = state.modules.reduce((sum, moduleId) => sum + modulePrices[moduleId], 0);
  const complexityMultiplier = 1 + (state.complexity - 1) * 0.18;
  const total = Math.round((base + modulesTotal) * complexityMultiplier);
  return {
    projectType: state.projectType,
    modules: state.modules,
    complexity: state.complexity,
    total,
    payload: {
      project_type: state.projectType,
      selected_modules: state.modules,
      complexity: state.complexity,
      estimated_budget: total,
    },
  };
}

function render() {
  const report = estimate(state);
  complexityValue.textContent = `Сложность: ${state.complexity} / 5`;
  quoteSummary.textContent = JSON.stringify(report, null, 2);
}

projectTypeButtons.forEach((button) => {
  button.addEventListener("click", () => {
    state.projectType = button.dataset.type;
    render();
  });
});

moduleCheckboxes.forEach((checkbox) => {
  checkbox.addEventListener("change", () => {
    state.modules = Array.from(moduleCheckboxes).filter((item) => item.checked).map((item) => item.value);
    render();
  });
});

complexityInput.addEventListener("input", () => {
  state.complexity = Number(complexityInput.value);
  render();
});

render();
