import { TestBed } from '@angular/core/testing';
import { VisitorService } from './visitor.service';

describe('VisitorService', () => {
  let service: VisitorService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(VisitorService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  it('should return visitor stats', (done) => {
    service.getStats().subscribe(stats => {
      expect(stats).toBeDefined();
      expect(stats.totalModels).toBeGreaterThan(0);
      expect(stats.totalDatasets).toBeGreaterThan(0);
      done();
    });
  });
});
