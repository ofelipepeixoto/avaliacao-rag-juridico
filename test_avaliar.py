import unittest

from avaliar import carregar, medir, recuperar


class TestAvaliacao(unittest.TestCase):
    def test_reproduz_falso_positivo_de_multa(self):
        self.assertEqual(recuperar("Quanto é a multa de rescisão?"), "rescisao")

    def test_equivalencias_ajudam_no_desenvolvimento(self):
        self.assertIsNone(recuperar("Quando começa?"))
        self.assertEqual(recuperar("Quando começa?", expandir=True), "prazo")

    def test_relatorio_expoe_categorias_e_erros_da_reserva(self):
        resultado = medir(carregar("reserva.json"), expandir=True)
        self.assertEqual(resultado["total"], 4)
        self.assertIn("trecho_insuficiente", resultado["por_categoria"])
        self.assertLess(resultado["acertos"], resultado["total"])


if __name__ == "__main__":
    unittest.main()
