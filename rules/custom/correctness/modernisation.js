function browserRequests() {
  // ruleid: frappe-synchronous-browser-request
  frappe.call({method: "app.read", async: false});
  // ruleid: frappe-synchronous-browser-request
  $.ajax({url: "/api/method/app.read", async: false});
  // ruleid: frappe-synchronous-browser-request
  jQuery.ajax("/api/method/app.read", {async: false});
  // ruleid: frappe-synchronous-browser-request
  $.ajax("/api/method/app.read", {async: false});
  // ruleid: frappe-synchronous-browser-request
  jQuery.ajax({url: "/api/method/app.read", async: false});
  // ok: frappe-synchronous-browser-request
  frappe.call({method: "app.read", async: true});
  // ok: frappe-synchronous-browser-request
  frappe.call({method: "app.read"});
  // ok: frappe-synchronous-browser-request
  unrelated.call({async: false});
  // ok: frappe-synchronous-browser-request
  frappe.call({method: "app.read", args: {async: false}});
}

async function observedCompletion() {
  // ok: frappe-synchronous-browser-request
  const result = await frappe.call({method: "app.read"});
  return result.message;
}
