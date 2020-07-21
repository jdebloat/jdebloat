import org.junit.Test;
import static org.junit.Assert.assertEquals;

import edu.ucla.cs.onr.test.*;

public class ApplicationTest {
  @Test
  public void behaviorTest() {
    for (int i = 0; i < 100_000_000; i++) {
      assertEquals(Application.doubleOrSquare(3, true), 6);
    }
  }
}
