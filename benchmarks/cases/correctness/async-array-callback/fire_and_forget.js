function warm_cache(rows) {
	rows.forEach((row) => {
		void frappe.call("example.api.warm_cache", { name: row.name });
	});
}
