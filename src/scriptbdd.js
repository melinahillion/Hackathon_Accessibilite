// URL of the JSON file
const jsonUrl = "../acceslibre_agglo_blois.json"; // Adjust the path as needed

// Target container for displaying results
const resultsContainer = document.getElementById("results-container");

// Fetch and process the JSON file
fetch(jsonUrl)
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        // Assuming data is an array of objects
        const bloisData = data.filter(item => item.commune === "Blois");

        // Clear the default loading message
        resultsContainer.innerHTML = "";

        // If no matches are found, display a message
        if (bloisData.length === 0) {
            const noResults = document.createElement("p");
            noResults.className = "no-results";
            noResults.textContent = "No results found for 'Blois'.";
            resultsContainer.appendChild(noResults);
            return;
        }

        // Create a result card for each matching item
        bloisData.forEach(item => {
            const {
                name,
                latitude,
                longitude,
                site_internet: siteInternet,
                voie,
                numero,
                postal_code,
            } = item;

            // Create a result container
            const resultDiv = document.createElement("div");
            resultDiv.className = "result";

            // Add content to the result container
            resultDiv.innerHTML = `
                <h2>${name || "Unknown Name"}</h2>
                <p><strong>Address:</strong> ${numero ? numero + " " : ""}${voie}, ${postal_code}</p>
                <p><strong>Commune:</strong> Blois</p>
                <p><strong>Latitude:</strong> ${latitude}</p>
                <p><strong>Longitude:</strong> ${longitude}</p>
                <p><strong>Site Internet:</strong> 
                    ${siteInternet
                        ? `<a href="${siteInternet}" target="_blank">${siteInternet}</a>`
                        : "No site available"}
                </p>
            `;

            // Append the result to the container
            resultsContainer.appendChild(resultDiv);
        });
    })
    .catch(error => {
        console.error("Error fetching or processing JSON:", error);

        // Display an error message in the container
        resultsContainer.innerHTML = `<p class="no-results">Error loading data. Please try again later.</p>`;
    });
