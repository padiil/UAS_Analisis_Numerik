// Sembunyikan tombol TOC di layar md ke atas
if (window.innerWidth >= 768) {
  document.getElementById("toc-toggle-btn").style.display = "none";
}
window.addEventListener("resize", function () {
  const tocToggleBtn = document.getElementById("toc-toggle-btn");
  if (window.innerWidth >= 768) {
    tocToggleBtn.style.display = "none";
  } else {
    tocToggleBtn.style.display = "block";
  }
});

// Toggle TOC di mobile
const tocBtn = document.getElementById("toc-toggle-btn");
const tocNav = document.getElementById("toc-navbar");
const tocCloseBtn = document.getElementById("toc-close-btn");
let tocVisible = false;
if (tocBtn && tocNav) {
  tocBtn.addEventListener("click", function () {
    tocVisible = true;
    tocNav.classList.remove("hidden");
    tocBtn.style.display = "none";
  });
  if (tocCloseBtn) {
    tocCloseBtn.addEventListener("click", function () {
      tocVisible = false;
      tocNav.classList.add("hidden");
      tocBtn.style.display = "block";
    });
  }
  // Sembunyikan TOC setelah klik link di mobile
  tocNav.querySelectorAll("a").forEach((link) => {
    link.addEventListener("click", function () {
      if (window.innerWidth < 768) {
        tocNav.classList.add("hidden");
        tocVisible = false;
        tocBtn.style.display = "block";
      }
    });
  });
}

// Toggle sumber data
const toggleBtn = document.getElementById("toggle-sumber-btn");
const sumberSection = document.getElementById("sumber-data-section");
let sumberVisible = false;
toggleBtn.addEventListener("click", function () {
  sumberVisible = !sumberVisible;
  sumberSection.classList.toggle("hidden", !sumberVisible);
  toggleBtn.textContent = sumberVisible
    ? "Sembunyikan Semua Sumber Data"
    : "Tampilkan Semua Sumber Data";
});

// Data dari Flask
var predictions = window.predictions;
var pdrb_data = window.pdrb_data;

var margin = { top: 20, right: 30, bottom: 40, left: 50 },
  width = 600 - margin.left - margin.right,
  height = 300 - margin.top - margin.bottom;

function drawGraph(historicalData, predictedData, containerId) {
  d3.select("#" + containerId).html("");

  var container = d3.select("#" + containerId);
  var containerWidth = container.node().getBoundingClientRect().width;
  var containerHeight =
    window.innerWidth < 640
      ? 220
      : container.node().getBoundingClientRect().height;

  var width = containerWidth - margin.left - margin.right;
  var height = containerHeight - margin.top - margin.bottom;

  var combinedData = historicalData.concat(predictedData);

  if (
    !combinedData ||
    combinedData.length === 0 ||
    (historicalData.length > 0 && typeof historicalData[0][0] === "string")
  ) {
    d3.select("#" + containerId).html(
      "<p class='text-red-500 text-center'>Tidak cukup data untuk menampilkan grafik.</p>"
    );
    return;
  }

  var svg = d3
    .select("#" + containerId)
    .append("svg")
    .attr("width", "100%")
    .attr("height", containerHeight + margin.bottom + margin.top)
    .attr(
      "viewBox",
      `0 0 ${width + margin.left + margin.right} ${
        height + margin.top + margin.bottom
      }`
    )
    .attr("preserveAspectRatio", "xMinYMin meet")
    .append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

  var x = d3
    .scaleLinear()
    .domain(
      d3.extent(combinedData, function (d) {
        return d[0];
      })
    )
    .range([0, width]);
  svg
    .append("g")
    .attr("transform", "translate(0," + height + ")")
    .call(d3.axisBottom(x).tickFormat(d3.format("d")));

  var yMin = d3.min(combinedData, function (d) {
    return d[1];
  });
  var yMax = d3.max(combinedData, function (d) {
    return d[1];
  });
  var yPaddingTop = (yMax - yMin) * 0.05;
  var yPaddingBottom = (yMax - yMin) * 0.1;

  var y = d3
    .scaleLinear()
    .domain([yMin - yPaddingBottom, yMax + yPaddingTop])
    .range([height, 0]);
  svg.append("g").call(d3.axisLeft(y).ticks(5));

  // Garis Historis
  var lineHistorical = d3
    .line()
    .x(function (d) {
      return x(d[0]);
    })
    .y(function (d) {
      return y(d[1]);
    });

  svg
    .append("path")
    .datum(historicalData)
    .attr("class", "line stroke-blue-500 stroke-2")
    .attr("d", lineHistorical);

  // Titik-titik data historis
  var historicalDots = svg
    .selectAll(".dot-historical")
    .data(historicalData)
    .enter()
    .append("circle")
    .attr("r", 5)
    .attr("cx", function (d) {
      return x(d[0]);
    })
    .attr("cy", function (d) {
      return y(d[1]);
    })
    .attr("class", "dot fill-blue-500 stroke-white stroke-1.5");

  // Garis Prediksi
  var linePredicted = d3
    .line()
    .x(function (d) {
      return x(d[0]);
    })
    .y(function (d) {
      return y(d[1]);
    });

  var lastHistoricalYear = d3.max(historicalData, function (d) {
    return d[0];
  });
  var filteredPredictedData = predictedData.filter(function (d) {
    return d[0] > lastHistoricalYear;
  });
  var combinedPredictedData = [];
  if (historicalData.length > 0) {
    combinedPredictedData.push(historicalData[historicalData.length - 1]);
  }
  combinedPredictedData = combinedPredictedData.concat(filteredPredictedData);

  if (combinedPredictedData.length > 1) {
    svg
      .append("path")
      .datum(combinedPredictedData)
      .attr("class", "line-predicted stroke-orange-500 stroke-2 stroke-dashed")
      .attr("d", linePredicted);
  }

  // Titik-titik data prediksi
  svg
    .selectAll(".dot-predicted")
    .data(filteredPredictedData)
    .enter()
    .append("circle")
    .attr("r", 5)
    .attr("cx", function (d) {
      return x(d[0]);
    })
    .attr("cy", function (d) {
      return y(d[1]);
    })
    .attr("class", "dot-predicted fill-orange-500 stroke-white stroke-1.5")
    .on("mouseover", function (event, d) {
      tooltip.transition().duration(200).style("opacity", 0.9);
      tooltip
        .html(
          "Tahun (Prediksi): " +
            d[0] +
            "<br/>Pertumbuhan: " +
            d3.format(".2f")(d[1]) +
            "%"
        )
        .style("left", event.pageX + 10 + "px")
        .style("top", event.pageY - 28 + "px");
    })
    .on("mouseout", function (d) {
      tooltip.transition().duration(500).style("opacity", 0);
    });

  // Tooltip
  var tooltip = d3
    .select("body")
    .append("div")
    .attr(
      "class",
      "absolute z-10 p-2 text-sm leading-none text-white whitespace-no-wrap bg-gray-800 rounded shadow-md opacity-0 transition-opacity duration-200 pointer-events-none"
    );

  // Label Sumbu X
  svg
    .append("text")
    .attr(
      "transform",
      "translate(" + width / 2 + " ," + (height + margin.top + 20) + ")"
    )
    .attr("class", "text-gray-600 text-sm")
    .style("text-anchor", "middle")
    .text("Tahun");

  // Label Sumbu Y
  svg
    .append("text")
    .attr("transform", "rotate(-90)")
    .attr("y", 0 - margin.left)
    .attr("x", 0 - height / 2)
    .attr("dy", "1em")
    .attr("class", "text-gray-600 text-sm")
    .style("text-anchor", "middle")
    .text("Pertumbuhan (%)");
}

// Gambar grafik nasional
if (predictions && predictions.Nasional && pdrb_data && pdrb_data.Nasional) {
  drawGraph(pdrb_data.Nasional, predictions.Nasional, "national-graph");
}
// Gambar grafik per provinsi
if (predictions && pdrb_data) {
  var i = 1;
  for (var provinsi in predictions) {
    if (provinsi !== "Nasional" && pdrb_data[provinsi]) {
      var containerId = "graph-" + i;
      drawGraph(pdrb_data[provinsi], predictions[provinsi], containerId);
      i++;
    }
  }
}
