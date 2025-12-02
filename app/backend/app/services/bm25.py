import math

class BM25:
    def __init__(self, N : int, avgdl : float, k1 : float = 1.5, b : float = 0.75):
        self.N = N          # nombre total de documents
        self.avgdl = avgdl  # longueur moyenne des documents
        self.k1 = k1
        self.b = b

    def idf(self, n : int) -> float:
        """
        n = nombre de documents contenant le mot
        """
        return math.log(((self.N - n + 0.5) / (n + 0.5)) + 1)

    def score(self, dl : int, tf : float, n : int) -> float:
        """
        dl = longueur du document
        tf = fréquence du mot dans ce document
        n  = nombre de documents contenant ce mot
        """
        idf = self.idf(n)
        denom = tf + self.k1 * (1 - self.b + self.b * dl / self.avgdl)
        return idf * (tf * (self.k1 + 1)) / denom

    def score_query(self, doc: dict) -> float:
        """
        doc : {
            "word_count": int,
            "words": {
                "token1": {"frequency": float, "number_documents": int},
                "token2": {"frequency": float, "number_documents": int},
                ...
            }
        }
        """
        total = 0.0
        for token, info in doc["words"].items():
            tf = info["frequency"]
            n = info["number_documents"]
            total += self.score(doc["word_count"], tf, n)
        return total

