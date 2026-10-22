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

function callbackParameterBoundaries(rows) {
  rows.forEach((row, index) => {
    // ruleid: frappe-client-request-in-array-callback
    frappe.call("work", {row, index});
  });
  rows.map(async (row, index, array) => {
    // ruleid: frappe-client-request-in-array-callback
    await frappe.xcall("work", {row, index, count: array.length});
  });
  rows.forEach(function(row, index) {
    // ruleid: frappe-client-request-in-array-callback
    frappe.db.get_value("ToDo", row.name, "status");
  });
  rows.map((row, index) => {
    // ok: frappe-client-request-in-array-callback
    return {row, index};
  });
  // ok: frappe-client-request-in-array-callback
  frappe.call("batch", {rows});
}

function additionalIterationForms(rows, context) {
  do {
    // ruleid: frappe-client-request-in-loop
    frappe.call("work");
  } while (pending());
  rows.forEach(row => {
    // ruleid: frappe-client-request-in-array-callback
    frappe.call("work", {row});
  }, context);
  rows.map(function(row) {
    // ruleid: frappe-client-request-in-array-callback
    return frappe.xcall("work", {row});
  }, context);
  rows.forEach(row => {
    // ok: frappe-client-request-in-array-callback
    localWork(row);
  }, context);
  // ok: frappe-client-request-in-loop
  frappe.call("batch", {rows});
}


function deferredRequests(rows, pending) {
  rows.forEach(row => {
    // ok: frappe-client-request-in-array-callback
    const fetchLater = () => frappe.call("work", {row});
    pending.push(fetchLater);
    // ruleid: frappe-client-request-in-array-callback
    frappe.call("work", {row});
  });
}


function nestedCallbackBoundaries(rows, pending, enabled) {
  rows.map(row => {
    function fetchLater() {
      // ok: frappe-client-request-in-array-callback
      return frappe.xcall("work", {row});
    }
    pending.push(fetchLater);
    if (enabled) {
      // ruleid: frappe-client-request-in-array-callback
      return frappe.xcall("work", {row});
    }
  });
  // ruleid: frappe-client-request-in-array-callback
  rows.map(row => frappe.call("work", {row}));
}
