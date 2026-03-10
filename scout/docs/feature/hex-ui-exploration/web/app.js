const SNAPSHOT_URL = "./data/fire-protection-los-angeles.json";

function money(value) {
  if (value == null) return "—";
  if (value >= 1000000) return `$${(value / 1000000).toFixed(1)}M`;
  return `$${Math.round(value).toLocaleString()}`;
}

function fullMoney(value) {
  if (value == null) return "—";
  return `$${Math.round(value).toLocaleString()}`;
}

function byReviews(a, b) {
  return (b.reviews || 0) - (a.reviews || 0);
}

function businessSignal(business) {
  return `${business.city} · ${business.reviews} reviews`;
}

function pickSelectedBusiness(businesses) {
  return (
    businesses.find((business) => business.name === "CITY OF ANGELS FIRE PROTECTION") ||
    businesses[0] ||
    null
  );
}

function pickSavedBusinesses(snapshot) {
  const saved = new Set(snapshot.saved_business_names || []);
  return snapshot.businesses.filter((business) => saved.has(business.name));
}

function pickSavedListings(snapshot) {
  const saved = new Set(snapshot.saved_listing_ids || []);
  return snapshot.listings.filter((listing) => saved.has(listing.source_id));
}

function renderHome(snapshot) {
  document.getElementById("home-query").textContent = snapshot.query;
  document.getElementById("home-business-count").textContent = `${snapshot.businesses.length} businesses`;
  document.getElementById("home-listing-count").textContent = `${snapshot.listings.length} listing${snapshot.listings.length === 1 ? "" : "s"} for sale`;
}

function renderResults(snapshot) {
  const businesses = [...snapshot.businesses].sort(byReviews);
  const listings = snapshot.listings || [];
  const selectedBusiness = pickSelectedBusiness(businesses);
  const selectedListing = listings[0] || null;

  document.getElementById("results-query").textContent = snapshot.query;
  document.getElementById("results-summary").textContent = `${businesses.length} businesses. ${listings.length} listing${listings.length === 1 ? "" : "s"} for sale.`;

  const businessRows = businesses
    .map((business) => {
      const selected = selectedBusiness && selectedBusiness.name === business.name ? ' class="selected"' : "";
      return `
        <tr${selected}>
          <td>
            <span class="row-primary">${business.name}</span>
            <span class="row-secondary">${business.rating.toFixed(1)} rating</span>
          </td>
          <td>${business.city}</td>
          <td>${business.reviews}</td>
          <td>${business.phone}</td>
        </tr>
      `;
    })
    .join("");
  document.getElementById("business-table-body").innerHTML = businessRows;

  const listingRows = listings
    .map(
      (listing) => `
        <tr class="signal">
          <td>
            <span class="row-primary">${listing.name}</span>
            <span class="row-secondary attention">For sale now</span>
          </td>
          <td>${listing.location.replace(", CA", "")}</td>
          <td>${money(listing.asking_price)}</td>
        </tr>
      `
    )
    .join("");
  document.getElementById("listing-table-body").innerHTML = listingRows || `
    <tr>
      <td colspan="3">No matching listings.</td>
    </tr>
  `;

  document.getElementById("listing-empty").textContent =
    listings.length === 1
      ? "Only one listing matched this search. That should read as useful context, not as a problem the UI needs to hide."
      : "No listings matched this search.";

  if (selectedBusiness) {
    document.getElementById("detail-business-name").textContent = selectedBusiness.name;
    document.getElementById("detail-business-address").textContent = selectedBusiness.address;
    document.getElementById("detail-business-phone").textContent = selectedBusiness.phone;
    document.getElementById("detail-business-website").textContent = selectedBusiness.website.replace(/^https?:\/\//, "");
    document.getElementById("detail-business-reviews").textContent = String(selectedBusiness.reviews);
    document.getElementById("detail-business-copy").textContent = `${selectedBusiness.city} lead with ${selectedBusiness.reviews} public reviews and a reachable website and phone number.`;
  }

  if (selectedListing) {
    document.getElementById("detail-listing-name").textContent = selectedListing.name;
    document.getElementById("detail-listing-location").textContent = selectedListing.location;
    document.getElementById("detail-listing-price").textContent = fullMoney(selectedListing.asking_price);
    document.getElementById("detail-listing-cashflow").textContent = fullMoney(selectedListing.cash_flow);
    document.getElementById("detail-listing-multiple").textContent = `${selectedListing.asking_multiple}x`;
    document.getElementById("detail-listing-copy").textContent =
      "Market context only. The product should not imply this listing is the same business as the selected lead unless the data proves it.";
  }
}

function renderSaved(snapshot) {
  const businesses = pickSavedBusinesses(snapshot);
  const listings = pickSavedListings(snapshot);

  document.getElementById("saved-summary").textContent = `A short list from run ${snapshot.run_id}. Keep only what deserves discussion.`;

  const businessRows = businesses
    .map((business, index) => {
      const status = index === 0 ? "Needs attention" : "Review later";
      const statusClass = index === 0 ? "attention" : "";
      return `
        <tr${index === 0 ? ' class="selected"' : ""}>
          <td>
            <span class="row-primary">${business.name}</span>
            <span class="row-secondary">${businessSignal(business)}</span>
          </td>
          <td>${business.city === "Los Angeles" ? "Local lead" : "Nearby lead"}</td>
          <td class="${statusClass}">${status}</td>
        </tr>
      `;
    })
    .join("");
  document.getElementById("saved-business-table-body").innerHTML = businessRows;

  const listingRows = listings
    .map(
      (listing) => `
        <tr class="signal">
          <td>
            <span class="row-primary">${listing.name}</span>
            <span class="row-secondary">${listing.location} · cash flow ${fullMoney(listing.cash_flow)}</span>
          </td>
          <td>${money(listing.asking_price)}</td>
          <td class="attention">Market comp</td>
        </tr>
      `
    )
    .join("");
  document.getElementById("saved-listing-table-body").innerHTML = listingRows;
}

async function main() {
  const page = document.body.dataset.page;
  const response = await fetch(SNAPSHOT_URL);
  const snapshot = await response.json();

  if (page === "home") {
    renderHome(snapshot);
  }
  if (page === "results") {
    renderResults(snapshot);
  }
  if (page === "saved") {
    renderSaved(snapshot);
  }
}

main().catch((error) => {
  console.error("Failed to load Scout UI snapshot", error);
});
