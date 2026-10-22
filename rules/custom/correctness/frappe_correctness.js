async function processRows(rows) {
  // ruleid: frappe-async-foreach-callback
  rows.forEach(async (row) => {
    await frappe.call("app.api.process", { name: row.name });
  });

  // ruleid: frappe-async-array-callback-misuse
  const visible = rows.filter(async function (row) {
    return await frappe.db.exists("ToDo", row.name);
  });

  // ruleid: frappe-async-array-callback-misuse
  const found = rows.find(async (row) => await canRead(row));

  // ruleid: frappe-async-array-callback-misuse
  const any = rows.some(async (row) => await canRead(row));

  // ruleid: frappe-async-array-callback-misuse
  const all = rows.every(async (row) => await canRead(row));

  // ruleid: frappe-async-array-callback-misuse
  rows.sort(async (left, right) => (await score(left)) - (await score(right)));

  return { visible, found, any, all };
}

async function validAsyncIteration(rows) {
  // ok: frappe-async-array-callback-misuse
  // ok: frappe-async-foreach-callback
  await Promise.all(rows.map(async (row) => frappe.call("app.api.process", { name: row.name })));

  // ok: frappe-async-array-callback-misuse
  for (const row of rows) {
    await frappe.call("app.api.process", { name: row.name });
  }
}

function independentDomUpdates(keys) {
  // ruleid: frappe-async-foreach-callback
  keys.forEach(async (key) => {
    document.querySelector(`[data-key="${key}"]`).textContent = await getTitle(key);
  });
}

// Inline callback matching must tolerate comments and formatting.
function callbackForms(rows) {
  // ruleid: frappe-async-foreach-callback
  rows.forEach(/* explanation */ async (row) => { await work(row); });
  // ruleid: frappe-async-foreach-callback
  rows.forEach(/* explanation */ async function (row) { await work(row); });
  // ruleid: frappe-async-foreach-callback
  rows.forEach(
    /* explanation */ async row => work(row)
  );
  // ruleid: frappe-async-array-callback-misuse
  rows.filter(/* explanation */ async row => canRead(row));
  // ruleid: frappe-async-array-callback-misuse
  rows.find(/* explanation */ async function (row) { return canRead(row); });
  // ruleid: frappe-async-array-callback-misuse
  rows.some(
    /* explanation */ async (row) => { return canRead(row); }
  );
  // ruleid: frappe-async-array-callback-misuse
  rows.every(/* explanation */ async function check(row) { return canRead(row); });
  // ruleid: frappe-async-array-callback-misuse
  rows.sort(/* explanation */ async (a, b) => score(a) - score(b));

  // ok: frappe-async-foreach-callback
  rows.forEach(/* explanation */ row => workSynchronously(row));
  // ok: frappe-async-array-callback-misuse
  rows.filter(/* explanation */ row => row.enabled);
  // ok: frappe-async-array-callback-misuse
  rows.find(row => row.enabled);
  // ok: frappe-async-array-callback-misuse
  rows.some(row => row.enabled);
  // ok: frappe-async-array-callback-misuse
  rows.every(row => row.enabled);
  // ok: frappe-async-array-callback-misuse
  rows.sort((a, b) => a.rank - b.rank);
}

function keywordBoundaries(rows) {
  // ok: frappe-async-foreach-callback
  rows.forEach(async => workSynchronously(async));
  // ok: frappe-async-array-callback-misuse
  rows.filter(async /* parameter, not keyword */ => async.enabled);
  // ruleid: frappe-async-foreach-callback
  rows.forEach(async /* keyword */ (row) => work(row));
  // ruleid: frappe-async-array-callback-misuse
  rows.filter(async /* keyword */ row => canRead(row));
}
