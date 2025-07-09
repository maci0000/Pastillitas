function buscar() {
    const query = document.getElementById('busqueda').value.trim();

    if (!query) {
        document.getElementById("mensaje").innerText = "Ingresa un nombre o principio activo.";
        return;
    }

    fetch(`/buscar?query=${encodeURIComponent(query)}`)
        .then(response => response.json())
        .then(data => {
            const tabla = document.getElementById('resultados');
            const tbody = tabla.querySelector('tbody');
            tbody.innerHTML = '';

            if (data.length === 0) {
                tabla.style.display = 'none';
                document.getElementById("mensaje").innerText = `No se encontraron resultados para "${query}"`;
            } else {
                tabla.style.display = 'table';
                document.getElementById("mensaje").innerText = '';
                data.forEach(row => {
                    const tr = document.createElement('tr');
                    tr.innerHTML = `
                        <td>${row.nombre_comercial}</td>
                        <td>${row.principio_activo}</td>
                        <td>S/ ${row.precio}</td>
                        <td>${row.farmacia}</td>
                    `;
                    tbody.appendChild(tr);
                });
            }
        })
        .catch(error => {
            console.error("Error en la búsqueda:", error);
            document.getElementById("mensaje").innerText = "Error al buscar. Revisa tu servidor.";
        });
}