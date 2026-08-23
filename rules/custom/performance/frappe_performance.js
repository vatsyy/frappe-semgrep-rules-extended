async function serialRequests(names) {
  for (const name of names) {
    // ruleid: frappe-client-request-in-loop
    await frappe.call("app.api.read", { name });
  }
}

function callbackRequests(names) {
  names.forEach((name) => {
    // ruleid: frappe-client-request-in-array-callback
    frappe.db.get_doc("ToDo", name);
  });
}

async function batchIsOk(names) {
  // ok: frappe-client-request-in-loop
  return frappe.call("app.api.read_many", { names });
}

function requestOutsideArrayCallbackIsOk(name) {
  // ok: frappe-client-request-in-array-callback
  return frappe.db.get_doc("ToDo", name);
}
