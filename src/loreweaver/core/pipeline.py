# SourceAdapter -> Classifier -> Transformer -> Indexer


from loreweaver.core.interfaces import Classifier, Indexer, SourceAdapter, Transformer
from loreweaver.core.models import Document


class IndexingPipeline:
    def __init__(
        self,
        source: SourceAdapter,
        classifier: Classifier,
        transformer: Transformer,
        indexer: Indexer,
    ): 
        self.source = source
        self.classifier = classifier
        self.transformer = transformer
        self.indexer = indexer


    def run(self):
        for artifact in self.source.collect():
            classification = self.classifier.classify(artifact)
            document = Document(
                artifact=artifact,
                classification=classification,
            )
            chunks = self.transformer.transform(document)
            self.indexer.index_chunks(chunks)