import org.junit.Test;
import static org.junit.Assert.assertEquals;

import java.io.IOException;
import edu.ucla.cs.onr.test.*;

public class ApplicationTest {
  @Test public void behaviorTest() {
    for (int i = 0; i < 10_000_000; i++) {
      assertEquals(Application.doubleOrSquare(3, true), 6);
    }
  }
}
