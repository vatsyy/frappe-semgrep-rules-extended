async function calculate_total(rows) {
	const amounts = await Promise.all(rows.map((row) => fetch_amount(row.name)));
	return amounts.reduce((total, amount) => total + amount, 0);
}
