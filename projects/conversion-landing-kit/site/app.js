const quizResult = document.querySelector("#quiz-result");
const submitState = document.querySelector("#submit-state");
const quizButtons = document.querySelectorAll("[data-answer]");
const form = document.querySelector("#lead-form");
const payloadPreview = document.querySelector("#payload-preview");
const analyticsFeed = document.querySelector("#analytics-feed");
const packageCard = document.querySelector("#package-card");

const analytics = [];
const STORAGE_KEY = "conversion-landing-kit:draft";
let selectedScenario = "landing";

const recommendations = {
  landing: {
    copy: "Подойдёт одностраничный сервисный лендинг с сильным первым экраном и короткой формой.",
    nextStep: "Собрать оффер, кейсы и форму в один сценарий.",
    packageName: "Lead Sprint",
    estimate: "от 45 000 ₽",
  },
  crm: {
    copy: "Имеет смысл сразу продумать payload заявки, webhook и антидубль на уровне лида.",
    nextStep: "Заложить структуру лида и карту полей под CRM.",
    packageName: "CRM Flow",
    estimate: "от 70 000 ₽",
  },
  telegram: {
    copy: "Лучше собирать форму так, чтобы менеджер сразу получал понятное уведомление в Telegram.",
    nextStep: "Собрать post-submit сценарий и уведомления.",
    packageName: "Telegram Assist",
    estimate: "от 60 000 ₽",
  },
  rescue: {
    copy: "Сначала нужен аудит текущей страницы: форма, события и post-submit сценарий.",
    nextStep: "Проверить утечки конверсии и сломанные события.",
    packageName: "Rescue Audit",
    estimate: "от 35 000 ₽",
  }
};

function track(eventName, payload) {
  const event = { eventName, payload, createdAt: new Date().toISOString() };
  analytics.push(event);
  renderAnalyticsFeed();
}

function renderAnalyticsFeed() {
  analyticsFeed.innerHTML = "";
  analytics.slice().reverse().forEach((event) => {
    const item = document.createElement("li");
    item.textContent = `${event.createdAt} — ${event.eventName}`;
    analyticsFeed.appendChild(item);
  });
}

function renderPackage(answer) {
  const recommendation = recommendations[answer];
  packageCard.textContent =
    `${recommendation.packageName}: ${recommendation.estimate}. ` +
    `Подходит, если нужен сценарий "${answer}" и важен быстрый переход к рабочему lead flow.`;
}

function saveDraft() {
  const formData = new FormData(form);
  const payload = Object.fromEntries(formData.entries());
  payload.scenario = selectedScenario;
  window.localStorage.setItem(STORAGE_KEY, JSON.stringify(payload));
}

function loadDraft() {
  const raw = window.localStorage.getItem(STORAGE_KEY);
  if (!raw) {
    renderPackage(selectedScenario);
    return;
  }
  const payload = JSON.parse(raw);
  Object.entries(payload).forEach(([key, value]) => {
    const field = form.elements.namedItem(key);
    if (field) {
      field.value = value;
    }
  });
  selectedScenario = payload.scenario || "landing";
  renderPackage(selectedScenario);
}

function buildLeadPayload(payload) {
  const recommendation = recommendations[selectedScenario];
  return {
    ...payload,
    summary: payload.summary.trim(),
    channel: "conversion-landing-kit",
    scenario: selectedScenario,
    packageName: recommendation.packageName,
    estimatedBudget: recommendation.estimate,
    createdAt: new Date().toISOString(),
    qualityScore: Math.min(100, 40 + payload.summary.length),
  };
}

function validatePayload(payload) {
  if (payload.name.trim().length < 2) {
    return "Введите имя без одной буквы.";
  }
  if (payload.summary.trim().length < 12) {
    return "Добавьте чуть больше деталей по задаче.";
  }
  return "";
}

quizButtons.forEach((button) => {
  button.addEventListener("click", () => {
    const answer = button.dataset.answer;
    selectedScenario = answer;
    track("quiz_answered", { answer });
    quizResult.textContent = `${recommendations[answer].copy} Следующий шаг: ${recommendations[answer].nextStep}`;
    renderPackage(answer);
    saveDraft();
  });
});

Array.from(form.elements).forEach((element) => {
  if (element.name) {
    element.addEventListener("input", saveDraft);
  }
});

form.addEventListener("submit", (event) => {
  event.preventDefault();
  const formData = new FormData(form);
  const rawPayload = Object.fromEntries(formData.entries());
  const validationError = validatePayload(rawPayload);
  if (validationError) {
    submitState.textContent = validationError;
    track("lead_validation_failed", { reason: validationError });
    return;
  }
  const payload = buildLeadPayload(rawPayload);
  track("lead_submitted", payload);
  payloadPreview.textContent = JSON.stringify(payload, null, 2);
  submitState.textContent = "Заявка сохранена в demo-режиме. Такой payload уже готов к отправке в CRM/API.";
  window.localStorage.removeItem(STORAGE_KEY);
  form.reset();
  renderPackage(selectedScenario);
});

loadDraft();
