import { Slider as BaseSlider } from "@base-ui/react/slider";
import styles from "./Slider.module.css";

export default function Slider({ value, onChange }) {
  return (
    <div className={styles.slider}>
      <label className={styles.value}>{`0`}</label>
      <BaseSlider.Root
        className={styles.sliderRoot}
        value={value}
        onValueChange={onChange}
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
      <label className={styles.value}>{`${value}%`}</label>
    </div>
  );
}
