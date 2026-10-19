const heroSlides = document.querySelectorAll(".hero-slide");
    let currentHeroSlide = 0;

    setInterval(() => {
      heroSlides[currentHeroSlide].classList.remove("active");

      currentHeroSlide =
        (currentHeroSlide + 1) % heroSlides.length;

      heroSlides[currentHeroSlide].classList.add("active");
    }, 5000);

        const historiaSlides =
      document.querySelectorAll(".historia-slide");

    let currentHistoriaSlide = 0;

    if (historiaSlides.length > 1) {
      setInterval(() => {
        historiaSlides[currentHistoriaSlide]
          .classList.remove("active");

        currentHistoriaSlide =
          (currentHistoriaSlide + 1) %
          historiaSlides.length;

        historiaSlides[currentHistoriaSlide]
          .classList.add("active");
      }, 5000);
    }

const dataDoCasamento =
      new Date("2026-09-26T10:30:00-03:00").getTime();

    const contadorDias =
      document.getElementById("contadorDias");

    const contadorHoras =
      document.getElementById("contadorHoras");

    const contadorMinutos =
      document.getElementById("contadorMinutos");

    const contadorSegundos =
      document.getElementById("contadorSegundos");

    const contagemCasamento =
      document.getElementById("contagemCasamento");

    const mensagemGrandeDia =
      document.getElementById("mensagemGrandeDia");

    let intervaloContagem = null;

    function atualizarContagemCasamento() {
      const agora = new Date().getTime();
      const tempoRestante = dataDoCasamento - agora;

      if (tempoRestante <= 0) {
        contagemCasamento.style.display = "none";
        mensagemGrandeDia.style.display = "block";

        if (intervaloContagem !== null) {
          clearInterval(intervaloContagem);
        }

        return;
      }

      const umSegundo = 1000;
      const umMinuto = umSegundo * 60;
      const umaHora = umMinuto * 60;
      const umDia = umaHora * 24;

      const dias =
        Math.floor(tempoRestante / umDia);

      const horas =
        Math.floor((tempoRestante % umDia) / umaHora);

      const minutos =
        Math.floor((tempoRestante % umaHora) / umMinuto);

      const segundos =
        Math.floor((tempoRestante % umMinuto) / umSegundo);

      contadorDias.textContent = dias;

      contadorHoras.textContent =
        String(horas).padStart(2, "0");

      contadorMinutos.textContent =
        String(minutos).padStart(2, "0");

      contadorSegundos.textContent =
        String(segundos).padStart(2, "0");
    }

    atualizarContagemCasamento();

    if (new Date().getTime() < dataDoCasamento) {
      intervaloContagem =
        setInterval(atualizarContagemCasamento, 1000);
    }
