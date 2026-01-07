document.addEventListener("DOMContentLoaded", () => {
  const counters = document.querySelectorAll(".metric-value");
  const circles = document.querySelectorAll(".overlap-progress");

  const easeOutExpo = (x) => (x === 1 ? 1 : 1 - Math.pow(2, -10 * x));

  const formatValue = (value) => {
    if (value < 1000) return value.toLocaleString("en-US");
    if (value < 10000) return value.toLocaleString("en-US");
    const units = [
      { value: 1e9, suffix: "B" },
      { value: 1e6, suffix: "M" },
      { value: 1e3, suffix: "k" },
    ];
    const unit = units.find((u) => value >= u.value);
    if (!unit) return value.toLocaleString("en-US");
    const scaled = value / unit.value;
    const rounded = scaled >= 10 ? Math.round(scaled) : Math.round(scaled * 10) / 10;
    return `${rounded}${unit.suffix}`;
  };

  counters.forEach((counter, index) => {
    const target = parseFloat(counter.dataset.target ?? "0");
    if (Number.isNaN(target)) return;
    const duration = 1600;
    const startDelay = index * 120;
    let startTime = null;

    const update = (timestamp) => {
      if (!startTime) startTime = timestamp;
      const elapsed = timestamp - startTime - startDelay;
      if (elapsed < 0) {
        requestAnimationFrame(update);
        return;
      }
      const progress = Math.min(elapsed / duration, 1);
      const eased = easeOutExpo(progress);
      let value = eased * target;
      if (counter.classList.contains("metric-percentage")) {
        counter.textContent = `${value.toFixed(2)}%`;
      } else {
        value = Math.floor(value);
        counter.textContent =
          value < 10000
            ? value.toLocaleString("en-US")
          : formatValue(value);
      }
      if (progress < 1) {
        requestAnimationFrame(update);
      }
    };

    requestAnimationFrame(update);
  });

  document.querySelectorAll(".copy-reference").forEach((btn) => {
    btn.addEventListener("click", () => {
      const code = btn.closest(".reference-entry")?.querySelector("code");
      const text = code?.textContent ?? "";
      navigator.clipboard.writeText(text).then(() => {
        btn.classList.add("copied");
        const original = btn.innerHTML;
        btn.textContent = "Copied!";
        setTimeout(() => {
          btn.classList.remove("copied");
          btn.innerHTML = original;
        }, 1200);
      });
    });
  });

  circles.forEach((circle) => {
    const target = parseFloat(circle.dataset.percentage ?? "0");
    const circumference = 2 * Math.PI * circle.r.baseVal.value;
    circle.style.strokeDasharray = `${circumference} ${circumference}`;
    circle.style.strokeDashoffset = circumference;

    const duration = 1600;
    let startTime = null;

    const animate = (timestamp) => {
      if (!startTime) startTime = timestamp;
      const progress = Math.min((timestamp - startTime) / duration, 1);
      const eased = easeOutExpo(progress);
      const offset = circumference - (target / 100) * circumference * eased;
      circle.style.strokeDashoffset = offset;
      if (progress < 1) requestAnimationFrame(animate);
    };

    requestAnimationFrame(animate);
  });

  const asForm = document.getElementById("as-checker-form");
  if (asForm) {
    const asInput = document.getElementById("asn-input");
    const resultBox = document.getElementById("as-checker-result");

    const showResult = (message, state) => {
      if (!resultBox) return;
      resultBox.textContent = message;
      resultBox.classList.add("visible");
      resultBox.classList.toggle("affected", state === "affected");
      resultBox.classList.toggle("safe", state === "safe");
      if (state === "error") {
        resultBox.classList.remove("affected", "safe");
      }
    };

    asForm.addEventListener("submit", (event) => {
      event.preventDefault();
      const value = asInput?.value.trim() ?? "";
      if (!/^\d+$/.test(value)) {
        showResult("Please enter a valid AS number.", "error");
        return;
      }
      fetch("/check_as", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ asn: value }),
      })
        .then((response) => {
          if (!response.ok) throw new Error("Invalid response");
          return response.json();
        })
        .then((data) => {
          if (data.affected) {
            showResult("Your AS is affected by routing loops!", "affected");
          } else {
            showResult("Your AS is not affected!", "safe");
          }
        })
        .catch(() => {
          showResult("Unable to check the AS right now. Please try again later.", "error");
        });
    });
  }
});
