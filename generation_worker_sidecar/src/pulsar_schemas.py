from pulsar.schema import Array, Float, Integer, Record, String, Map


class Txt2ImgGenerationOverrideSettings(Record):
    sd_model_checkpoint = String()


class Txt2ImgGenerationSettings(Record):
    prompt = String()
    negative_prompt = String()
    styles = Array(String())
    seed = Integer()
    sampler_name = String()
    batch_size = Integer()
    n_iters = Integer()
    steps = Integer()
    cfg_scale = Float()
    width = Integer()
    height = Integer()
    override_settings = Txt2ImgGenerationOverrideSettings()


class RequestedTxt2ImgGenerationEvent(Record):
    id = String()
    metadata = Map(String())
    generation_settings = Txt2ImgGenerationSettings()


class CompletedTxt2ImgGenerationEvent(Record):
    id = String()
    metadata = Map(String())
    s3_bucket = String()
    s3_object_key = String()
