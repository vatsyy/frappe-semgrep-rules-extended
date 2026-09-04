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
