const traducoes = {
  "pt-BR": {
    menuInicio: "Início",
    menuConfirmacao: "Confirmação",
    menuPresentes: "Presentes",
    menuFotos: "Fotos",
    menuInformacoes: "Informações",

    nossoDiaTitulo: "Nosso dia",
    confirmacaoTitulo: "Confirme sua presença",
    presentesTitulo: "Sugestões de presentes",

    galeriaTitulo: "Galeria de fotos",
    nossasFotosTitulo: "Nossas fotos",
    fotosCasamentoTitulo: "Fotos do casamento"
  },

  en: {
    menuInicio: "Home",
    menuConfirmacao: "RSVP",
    menuPresentes: "Gifts",
    menuFotos: "Photos",
    menuInformacoes: "Information",

    nossoDiaTitulo: "Our day",
    confirmacaoTitulo: "Confirm your attendance",
    presentesTitulo: "Gift suggestions",

    galeriaTitulo: "Photo gallery",
    nossasFotosTitulo: "Our photos",
    fotosCasamentoTitulo: "Wedding photos"
  }
};

function aplicarIdioma(idioma) {
  const idiomaEscolhido = traducoes[idioma] ? idioma : "pt-BR";

  document.querySelectorAll("[data-i18n]").forEach(elemento => {
    const chave = elemento.dataset.i18n;
    const traducao = traducoes[idiomaEscolhido][chave];

    if (traducao) {
      elemento.textContent = traducao;
    }
  });

  document.documentElement.lang = idiomaEscolhido;
  localStorage.setItem("idiomaCasamento", idiomaEscolhido);
}

document.querySelectorAll("[data-language]").forEach(botao => {
  botao.addEventListener("click", () => {
    aplicarIdioma(botao.dataset.language);
  });
});

const idiomaSalvo = localStorage.getItem("idiomaCasamento") || "pt-BR";
aplicarIdioma(idiomaSalvo);