import { Slider as BaseSlider } from "@base-ui/react/slider";
import styles from "./Slider.module.css";
import { useState } from "react";

export default function Slider() {
  const [valor, setValor] = useState(50);

  return (
    <div className={styles.slider}>
      <label className={styles.value}>{`0`}</label>
      <BaseSlider.Root
        className={styles.sliderRoot}
        defaultValue={50}
        value={valor}
        onValueChange={setValor}
        min={0}
        max={100}
      >
        <BaseSlider.Control className={styles.Control}>
          <BaseSlider.Track className={styles.Track}>
            <BaseSlider.Indicator className={styles.Indicator} />
            <BaseSlider.Thumb aria-label="Volume" className={styles.Thumb} />
          </BaseSlider.Track>
        </BaseSlider.Control>
      </BaseSlider.Root>
      <label className={styles.value}>{`${valor}%`}</label>
    </div>
  );
}
