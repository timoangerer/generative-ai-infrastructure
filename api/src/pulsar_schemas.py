from pulsar.schema import Float, Integer, Record, String, Map


class Txt2ImgGenerationSettings(Record):
    prompt = String()
    negative_prompt = String()
    seed = Integer()
    sampler_name = String()
    batch_size = Integer()
    n_iters = Integer()
    steps = Integer()
    cfg_scale = Float()
    width = Integer()
    height = Integer()
    model = String()


class RequestedTxt2ImgGenerationEvent(Record):
    id = String()
    metadata = Map(String())
    generation_settings = Txt2ImgGenerationSettings()
