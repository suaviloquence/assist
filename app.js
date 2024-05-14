async function name_map() {
	const res = await fetch("./institutions.json");
	const data = await res.json();

	const map = new Map();

	for (const { id, names } of data) {
		// i best programmer
		map.set(id.toString(), names[0].name);
	}

	return map;
}

$(async function() {
	const res = await fetch("./dept-all.json");
	const data = await res.json();

	const ge_data = await (await fetch("./dept-ge.json")).json();

	const depts = new Map();
	
	const names = await name_map();

	for (const [id, place] of Object.entries(data)) {
		for (const [dept, classes] of Object.entries(place)) {
			if (!depts.has(dept)) depts.set(dept, new Map());
			const map = depts.get(dept);
			for (const [cls, art] of Object.entries(classes)) {
				if (!map.has(cls)) map.set(cls, []);
				if (art) map.get(cls).push([id, art]);
			}
		}
	}

	const ge_map = new Map();

	for (const [id, ges] of Object.entries(ge_data)) {
		if (!ges) continue;
		for (const [ge, classes] of Object.entries(ges)) {
			if (classes.length === 0) continue;
			if (!ge_map.has(ge)) ge_map.set(ge, new Map());
			ge_map.get(ge).set(id, classes);
		}
	}


	depts.set("General Education", ge_map);

	const d_selector = $('#dept');
	const c_selector = $('#class');
	const results = $('#results');

	for (const [dept, _] of depts) {
		$(`<option value="${dept}">${dept}</option>`).appendTo(d_selector);
	}

	function c_change() {
		const dept = d_selector.val();
		const cls = c_selector.val();
		results.empty();

		let i = 0;
		for (const [id, art] of depts.get(dept).get(cls)) {
			let html = art;
			if (Array.isArray(art)) {
				html = "<ul>";
				for (const itm of art) {
					html += `<li>${itm}</li>`;
				}
				html += "</ul>";
			}

			$(`<li><span class="cc">${names.get(id)}</span> - ${html}</li>`).appendTo(results);
			i++;
		}
		if (i === 0) $(`<p>Sorry, no articulations found for this class.</p>`).appendTo(results);
	}

	function d_change() {
		const dept = d_selector.val();
		c_selector.empty();
		
		let i = 0;
		for (const [cls, _] of depts.get(dept)) {
			$(`<option value="${cls}">${cls}</option>`).appendTo(c_selector);	i++;
		}
	
		if (dept === "Writing") alert("If you are looking for WRIT 2, go to General Education -> Composition");

		if (i === 0) $(`<p>Sorry, no articulations found for this department.</p>`).appendTo(results);

		c_change();

	}
	


	d_selector.on('change', d_change);
	c_selector.on('change', c_change);

	d_change();
});
