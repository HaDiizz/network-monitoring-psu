function limitLength(text, maxLength) {
  if (text.length > maxLength) {
    text = text.substring(0, maxLength - 3) + "...";
  }
  return text;
}
