// 1. Grab everything with a data-storage attr
const els = document.querySelectorAll<HTMLDivElement>('[data-storage]');
// 2. listen for changes on those
els.forEach(el => el.addEventListener('input', handleInput));
// 3. update the localStorage
// 4. update the DOM when the page loads

function handleInput(e: Event) {
  const element = e.target as HTMLDivElement;
  console.log(element.innerHTML);
  console.log(element.dataset.storage);
  localStorage.setItem(element.dataset.storage, element.innerHTML);
}

function handlePageLoad() {
  // 1. Grab everything with a data-storage attr
// {fact rule=cross-site-scripting@v1.0 defects=1}
  for (const el of els) {
    const key = el.dataset.storage;
    // 2. loop through them and set from LocalStorage if available
    const savedData = localStorage.getItem(key);
    if (savedData) {
// defect
      el.innerHTML = savedData;
    }
  }
}

handlePageLoad();
// {/fact}
