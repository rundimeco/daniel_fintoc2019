import pickle
from baselines import vector_baseline

def choose_model(key):
  d = {x:"%s__DT10.txt.sav"%x for x in ["B%i"%y for y in range(1,7)]}
  if key in d:
    return d[key]
  else:
    return d["B3"]

def check_features_base(data):
  features_base = ["begins_with_numbering", "is_italic","is_all_caps", "begins_with_cap", "page_nb"]
  for feat in features_base:
    if feat not in data:
      return False
  return True

def select_BL(data):
  has_feature_base = check_features_base(data)
  if has_feature_base==True:
    BL_model = "B6"
  else:
    BL_model = "B3"
  return BL_model

def predict_title(data):
  ##data : "text_line" + basic_features
  results = []

  BL_model = select_BL(data)
  x = vector_baseline(data, BL_model)
  filename = "models/%s"%choose_model(BL_model)
  loaded_model = pickle.load(open(filename, 'rb'))
  is_title = loaded_model.predict_proba([x])[0][1]
  results.append([BL_model, is_title])

  return results

if __name__=="__main__":
  for text in ["Introduction", "Conclusion", "BOARD DIRECTORS", "Imamd test, échec. "*25]:
    data = {"text_line": text}
    print(text[:20])
    for item in predict_title(data):
      print("  ",item)
