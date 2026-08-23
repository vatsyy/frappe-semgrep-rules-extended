async function calculate_total(rows) {
	let total = 0;
	rows.forEach(async (row) => {
		total += await fetch_amount(row.name);
	});
	return total;
}
