async function loadRepository(repository, results) {
  const section = document.createElement("section");
  const heading = document.createElement("h2");
  const link = document.createElement("a");
  const url = new URL(`../../${encodeURIComponent(repository)}/ci/`, location.href);
  link.href = url.href;
  link.textContent = repository;
  heading.append(link);
  section.append(heading);
  const status = document.createElement("p");
  status.textContent = "読み込み中…";
  section.append(status);
  results.append(section);

  try {
    const response = await fetch(new URL("data.json", url));
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const records = await response.json();
    if (!Array.isArray(records) || records.some(record => record.repository !== `bgnori/${repository}`)) {
      throw new Error("データの形式またはリポジトリが不正です");
    }
    window.renderLeanMetrics(records, section, { showRepository: false });
    status.textContent = records.length ? `${records.length}件の結果` : "計測結果はまだありません。";
  } catch (error) {
    status.textContent = `読み込み失敗: ${error.message}`;
  }
}

fetch("repositories.json")
  .then(response => {
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return response.json();
  })
  .then(repositories => {
    if (!Array.isArray(repositories) || repositories.some(name => !/^[a-z0-9-]+$/.test(name))) {
      throw new Error("リポジトリ一覧が不正です");
    }
    document.querySelector("#status").textContent = "";
    return Promise.all(repositories.map(repository =>
      loadRepository(repository, document.querySelector("#results"))));
  })
  .catch(error => { document.querySelector("#status").textContent = `一覧の読み込み失敗: ${error.message}`; });
