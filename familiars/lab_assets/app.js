"use strict";

const CELL_WIDTH = 192;
const CELL_HEIGHT = 208;
const FRAME_MS = 135;

const model = {
  catalog: null,
  petsById: new Map(),
  statesById: new Map(),
  scene: [],
  selectedKey: null,
  pack: "all",
  query: "",
  globalState: "idle",
  theme: "familiars-dark",
  timers: [],
};

const images = new Map();
const elements = {
  clearButton: document.querySelector("#clear-button"),
  emptyState: document.querySelector("#empty-state"),
  exportButton: document.querySelector("#export-button"),
  globalStateStrip: document.querySelector("#global-state-strip"),
  libraryCount: document.querySelector("#library-count"),
  packSelect: document.querySelector("#pack-select"),
  petList: document.querySelector("#pet-list"),
  petStage: document.querySelector("#pet-stage"),
  rallyButton: document.querySelector("#rally-button"),
  removeButton: document.querySelector("#remove-button"),
  sceneCount: document.querySelector("#scene-count"),
  searchInput: document.querySelector("#search-input"),
  selectedDescription: document.querySelector("#selected-description"),
  selectedName: document.querySelector("#selected-name"),
  selectedSection: document.querySelector("#selected-section"),
  selectedStateGrid: document.querySelector("#selected-state-grid"),
  statusMessage: document.querySelector("#status-message"),
  surpriseButton: document.querySelector("#surprise-button"),
  themeList: document.querySelector("#theme-list"),
  themeName: document.querySelector("#theme-name"),
};

const thumbnailObserver = new IntersectionObserver(
  (entries) => {
    entries.forEach((entry) => {
      if (!entry.isIntersecting) {
        return;
      }
      const thumb = entry.target;
      thumb.style.backgroundImage = `url("${thumb.dataset.src}")`;
      thumbnailObserver.unobserve(thumb);
    });
  },
  { root: elements.petList, rootMargin: "120px 0px" },
);

function setStatus(message) {
  elements.statusMessage.textContent = message;
}

function titleCase(value) {
  return value
    .split("-")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");
}

function getSelected() {
  return model.scene.find((item) => item.key === model.selectedKey) || null;
}

function stopRitual() {
  model.timers.forEach((timer) => window.clearTimeout(timer));
  model.timers = [];
}

function loadImage(pet) {
  if (!images.has(pet.id)) {
    const image = new Image();
    image.src = pet.spritesheet;
    images.set(pet.id, image);
  }
  return images.get(pet.id);
}

function stateButton(state, active, onClick) {
  const button = document.createElement("button");
  button.className = "state-button";
  button.type = "button";
  button.textContent = titleCase(state.id);
  button.title = state.caption;
  button.setAttribute("aria-pressed", String(active));
  button.addEventListener("click", onClick);
  return button;
}

function renderGlobalStates() {
  elements.globalStateStrip.replaceChildren();
  model.catalog.states.forEach((state) => {
    elements.globalStateStrip.append(
      stateButton(state, state.id === model.globalState, () => {
        stopRitual();
        model.globalState = state.id;
        model.scene.forEach((item) => {
          item.state = state.id;
        });
        renderScene();
        renderGlobalStates();
        renderInspector();
        setStatus(`The whole council is now ${state.caption}.`);
      }),
    );
  });
}

function filteredPets() {
  const query = model.query.trim().toLowerCase();
  return model.catalog.pets.filter((pet) => {
    const inPack = model.pack === "all" || pet.packs.includes(model.pack);
    if (!inPack || !query) {
      return inPack;
    }
    return [
      pet.id,
      pet.displayName,
      pet.description,
      pet.subtitle,
      ...pet.tags,
    ].some((value) => String(value).toLowerCase().includes(query));
  });
}

function renderLibrary() {
  const pets = filteredPets();
  const activeIds = new Set(model.scene.map((item) => item.id));
  thumbnailObserver.disconnect();
  elements.petList.replaceChildren();
  elements.libraryCount.textContent = String(pets.length);

  pets.forEach((pet) => {
    const button = document.createElement("button");
    button.className = "pet-row";
    button.type = "button";
    button.setAttribute("role", "listitem");
    button.dataset.active = String(activeIds.has(pet.id));
    button.title = pet.description;
    button.addEventListener("click", () => addPet(pet.id));

    const thumb = document.createElement("span");
    thumb.className = "pet-thumb";
    thumb.dataset.src = pet.spritesheet;
    thumb.setAttribute("aria-hidden", "true");

    const copy = document.createElement("span");
    copy.className = "pet-copy";
    const name = document.createElement("strong");
    name.textContent = pet.displayName;
    const role = document.createElement("small");
    role.textContent = pet.subtitle || pet.tags.slice(0, 2).join(" / ") || "Familiar";
    copy.append(name, role);

    const sign = document.createElement("span");
    sign.className = "add-sign";
    sign.textContent = activeIds.has(pet.id) ? "" : "+";
    sign.setAttribute("aria-hidden", "true");
    button.append(thumb, copy, sign);
    elements.petList.append(button);
    thumbnailObserver.observe(thumb);
  });
}

function addPet(petId) {
  stopRitual();
  const existing = model.scene.find((item) => item.id === petId);
  if (existing) {
    model.selectedKey = existing.key;
    wavePet(existing);
    return;
  }
  if (model.scene.length >= model.catalog.limits.petsPerScene) {
    setStatus(`A scene holds up to ${model.catalog.limits.petsPerScene} familiars.`);
    return;
  }
  const pet = model.petsById.get(petId);
  const item = {
    key: `${petId}-${Date.now()}-${model.scene.length}`,
    id: petId,
    state: model.globalState,
    offset: Math.floor(Math.random() * 8),
  };
  model.scene.push(item);
  model.selectedKey = item.key;
  loadImage(pet);
  renderAll();
  setStatus(`${pet.displayName} joined the council.`);
}

function removeSelected() {
  const selected = getSelected();
  if (!selected) {
    return;
  }
  const pet = model.petsById.get(selected.id);
  model.scene = model.scene.filter((item) => item.key !== selected.key);
  model.selectedKey = model.scene.at(-1)?.key || null;
  renderAll();
  setStatus(`${pet.displayName} left the stage.`);
}

function clearScene() {
  stopRitual();
  model.scene = [];
  model.selectedKey = null;
  renderAll();
  setStatus("The stage is ready for a new council.");
}

function wavePet(item) {
  const restState = item.state;
  item.state = "waving";
  model.selectedKey = item.key;
  renderScene();
  renderInspector();
  const timer = window.setTimeout(() => {
    item.state = restState;
    renderScene();
    renderInspector();
  }, 900);
  model.timers.push(timer);
}

function scenePet(item) {
  const pet = model.petsById.get(item.id);
  const button = document.createElement("button");
  button.className = "stage-pet";
  button.type = "button";
  button.dataset.key = item.key;
  button.dataset.selected = String(item.key === model.selectedKey);
  button.setAttribute("aria-label", `${pet.displayName}, ${titleCase(item.state)}. Click to wave.`);
  button.addEventListener("click", () => wavePet(item));

  const canvas = document.createElement("canvas");
  canvas.width = CELL_WIDTH;
  canvas.height = CELL_HEIGHT;
  canvas.dataset.petKey = item.key;

  const label = document.createElement("span");
  label.className = "stage-pet-label";
  const name = document.createElement("strong");
  name.textContent = pet.displayName;
  const state = document.createElement("small");
  state.textContent = titleCase(item.state);
  label.append(name, state);
  button.append(canvas, label);
  return button;
}

function renderScene() {
  elements.petStage.replaceChildren();
  elements.petStage.dataset.count = String(model.scene.length);
  const columns = model.scene.length <= 4 ? Math.max(1, model.scene.length) : 3;
  elements.petStage.style.setProperty("--scene-columns", String(columns));
  model.scene.forEach((item) => elements.petStage.append(scenePet(item)));
  elements.emptyState.hidden = model.scene.length > 0;
  elements.sceneCount.textContent = `${model.scene.length} / ${model.catalog.limits.petsPerScene}`;
  elements.exportButton.disabled = model.scene.length === 0;
  elements.rallyButton.disabled = model.scene.length === 0;
  elements.clearButton.disabled = model.scene.length === 0;
}

function renderInspector() {
  const selected = getSelected();
  elements.selectedSection.hidden = !selected;
  if (!selected) {
    return;
  }
  const pet = model.petsById.get(selected.id);
  elements.selectedName.textContent = pet.displayName;
  elements.selectedDescription.textContent = pet.description;
  elements.selectedStateGrid.replaceChildren();
  model.catalog.states.forEach((state) => {
    elements.selectedStateGrid.append(
      stateButton(state, state.id === selected.state, () => {
        stopRitual();
        selected.state = state.id;
        renderScene();
        renderInspector();
        setStatus(`${pet.displayName} is now ${state.caption}.`);
      }),
    );
  });
}

function applyTheme(name) {
  const theme = model.catalog.themes[name];
  if (!theme) {
    return;
  }
  model.theme = name;
  const root = document.documentElement;
  root.style.setProperty("--stage-background", theme.background);
  root.style.setProperty("--stage-grid", theme.grid);
  root.style.setProperty("--stage-accent", theme.accent);
  root.style.setProperty("--stage-text", theme.text);
  elements.themeName.textContent = titleCase(name);
  renderThemes();
}

function renderThemes() {
  elements.themeList.replaceChildren();
  Object.entries(model.catalog.themes).forEach(([name, theme]) => {
    const button = document.createElement("button");
    button.className = "theme-option";
    button.type = "button";
    button.setAttribute("aria-pressed", String(name === model.theme));
    button.addEventListener("click", () => {
      applyTheme(name);
      setStatus(`${titleCase(name)} is live on stage.`);
    });

    const swatch = document.createElement("span");
    swatch.className = "theme-swatch";
    swatch.style.setProperty("--swatch-background", theme.background);
    swatch.style.setProperty("--swatch-accent", theme.accent);
    swatch.setAttribute("aria-hidden", "true");

    const copy = document.createElement("span");
    const title = document.createElement("strong");
    title.textContent = titleCase(name);
    const description = document.createElement("small");
    description.textContent = theme.description;
    copy.append(title, description);
    button.append(swatch, copy);
    elements.themeList.append(button);
  });
}

function chooseRandom(values, count) {
  const shuffled = [...values];
  for (let index = shuffled.length - 1; index > 0; index -= 1) {
    const target = Math.floor(Math.random() * (index + 1));
    [shuffled[index], shuffled[target]] = [shuffled[target], shuffled[index]];
  }
  return shuffled.slice(0, count);
}

function surprise() {
  stopRitual();
  const available = model.pack === "all"
    ? model.catalog.pets.map((pet) => pet.id)
    : model.catalog.packs[model.pack];
  const count = Math.min(4, available.length);
  model.scene = chooseRandom(available, count).map((id, index) => ({
    key: `${id}-${Date.now()}-${index}`,
    id,
    state: "idle",
    offset: index * 2,
  }));
  model.globalState = "idle";
  model.selectedKey = model.scene[0]?.key || null;
  model.scene.forEach((item) => loadImage(model.petsById.get(item.id)));
  renderAll();
  const label = model.pack === "all" ? "the full catalog" : titleCase(model.pack);
  setStatus(`The lab assembled a council from ${label}.`);
}

function scheduleState(delay, item, state) {
  const timer = window.setTimeout(() => {
    item.state = state;
    renderScene();
    renderInspector();
  }, delay);
  model.timers.push(timer);
}

function runRitual() {
  if (!model.scene.length) {
    return;
  }
  stopRitual();
  setStatus("Council ritual: hello, lift, work, review.");
  model.scene.forEach((item, index) => {
    scheduleState(index * 180, item, "waving");
    scheduleState(900 + index * 120, item, "jumping");
    scheduleState(1700 + index * 80, item, "running");
    scheduleState(2800 + index * 100, item, "review");
    scheduleState(4100, item, model.globalState);
  });
}

function recipeFromScene() {
  const beats = model.scene.map((item) => {
    const state = model.statesById.get(item.state);
    return {
      pet: item.id,
      beats: [{ state: item.state, caption: state.caption }],
    };
  });
  return {
    version: 1,
    title: "Familiars Lab Council",
    preset: model.scene.length > 1 ? "comparison" : "spotlight",
    theme: model.theme,
    slug: "familiars-lab-council",
    outputs: {
      formats: ["gif", "poster"],
      dir: "output/sequences",
    },
    scenes: [
      {
        layout: model.scene.length > 1 ? "comparison" : "spotlight",
        pets: beats,
      },
    ],
  };
}

async function exportRecipe() {
  if (!model.scene.length) {
    return;
  }
  const recipe = recipeFromScene();
  elements.exportButton.disabled = true;
  setStatus("Validating the scene with the Familiars renderer...");
  try {
    const response = await fetch("/api/validate-recipe", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(recipe),
    });
    const result = await response.json();
    if (!response.ok || !result.ok) {
      throw new Error(result.error || "Recipe validation failed.");
    }
    const form = document.createElement("form");
    form.method = "post";
    form.action = "/api/download-recipe";
    form.hidden = true;
    const input = document.createElement("input");
    input.type = "hidden";
    input.name = "recipe";
    input.value = JSON.stringify(recipe);
    form.append(input);
    document.body.append(form);
    form.submit();
    window.setTimeout(() => form.remove(), 1000);
    setStatus(`Validated and exported ${result.pets} familiar${result.pets === 1 ? "" : "s"}.`);
  } catch (error) {
    setStatus(`Export stopped: ${error.message}`);
  } finally {
    elements.exportButton.disabled = false;
  }
}

function renderAll() {
  renderLibrary();
  renderGlobalStates();
  renderScene();
  renderInspector();
}

function drawFrame(now) {
  document.querySelectorAll("canvas[data-pet-key]").forEach((canvas) => {
    const item = model.scene.find((candidate) => candidate.key === canvas.dataset.petKey);
    if (!item) {
      return;
    }
    const pet = model.petsById.get(item.id);
    const state = model.statesById.get(item.state);
    const image = loadImage(pet);
    if (!image.complete || !image.naturalWidth) {
      return;
    }
    const frame = (Math.floor(now / FRAME_MS) + item.offset) % state.frameCount;
    const context = canvas.getContext("2d");
    context.clearRect(0, 0, CELL_WIDTH, CELL_HEIGHT);
    context.drawImage(
      image,
      frame * CELL_WIDTH,
      state.row * CELL_HEIGHT,
      CELL_WIDTH,
      CELL_HEIGHT,
      0,
      0,
      CELL_WIDTH,
      CELL_HEIGHT,
    );
  });
  window.requestAnimationFrame(drawFrame);
}

function bindEvents() {
  elements.searchInput.addEventListener("input", (event) => {
    model.query = event.target.value;
    renderLibrary();
  });
  elements.packSelect.addEventListener("change", (event) => {
    model.pack = event.target.value;
    renderLibrary();
    setStatus(model.pack === "all" ? "Showing every familiar." : `Showing the ${titleCase(model.pack)} pack.`);
  });
  elements.surpriseButton.addEventListener("click", surprise);
  elements.rallyButton.addEventListener("click", runRitual);
  elements.exportButton.addEventListener("click", exportRecipe);
  elements.clearButton.addEventListener("click", clearScene);
  elements.removeButton.addEventListener("click", removeSelected);
}

async function start() {
  try {
    const response = await fetch("/api/catalog");
    if (!response.ok) {
      throw new Error(`Catalog request failed with ${response.status}.`);
    }
    model.catalog = await response.json();
    model.catalog.pets.forEach((pet) => model.petsById.set(pet.id, pet));
    model.catalog.states.forEach((state) => model.statesById.set(state.id, state));

    elements.packSelect.append(new Option("All familiars", "all"));
    Object.entries(model.catalog.packs).forEach(([name, ids]) => {
      elements.packSelect.append(new Option(`${titleCase(name)} (${ids.length})`, name));
    });

    bindEvents();
    renderThemes();
    applyTheme(model.theme);
    surprise();
    window.requestAnimationFrame(drawFrame);
  } catch (error) {
    setStatus(`The lab could not start: ${error.message}`);
  }
}

start();
